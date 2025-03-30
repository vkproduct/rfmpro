import http.server
import socketserver
import pandas as pd
from rfmpro_analysis import rfm_analysis
import os
import json
import traceback
from urllib.parse import unquote
from datetime import datetime

# Попытка инициализации Firebase, при условии наличия конфигурационного файла
firebase_admin_imported = False
try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore, storage
    
    # Проверяем наличие конфигурационного файла
    if os.path.exists("firebase_config.json"):
        cred = credentials.Certificate("firebase_config.json")
        try:
            # Пытаемся инициализировать Firebase с указанным bucket
            firebase_admin.initialize_app(cred, {"storageBucket": "rfmpro-ed06f.appspot.com"})
            db = firestore.client()
            bucket = storage.bucket()
            firebase_admin_imported = True
            print("Firebase успешно инициализирован")
        except Exception as e:
            print(f"Ошибка при инициализации Firebase: {str(e)}")
            # Попытка инициализации без указания конкретного bucket
            try:
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                # Не используем storage в этом случае
                firebase_admin_imported = True
                print("Firebase инициализирован без доступа к Storage")
            except Exception as e:
                print(f"Невозможно инициализировать Firebase: {str(e)}")
    else:
        print("Файл конфигурации Firebase не найден: firebase_config.json")
except ImportError:
    print("Модуль firebase_admin не установлен, функциональность Firebase будет отключена")

PORT = 8000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Запрос: GET {self.path}")
        
        if self.path == '/':
            print("GET / requested")
            try:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open("static/index.html", "rb") as f:
                    content = f.read()
                    print(f"Sending index.html, size: {len(content)} bytes")
                    self.wfile.write(content)
            except FileNotFoundError:
                print("index.html not found")
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"404 - File not found")
        
        elif self.path == '/style.css':
            print("GET /style.css requested")
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open("static/style.css", "rb") as f:
                self.wfile.write(f.read())
        
        elif self.path == '/dashboard':
            print("GET /dashboard requested")
            try:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open("static/dashboard/index.html", "rb") as f:
                    content = f.read()
                    print(f"Отправка dashboard/index.html, размер: {len(content)} байт")
                    self.wfile.write(content)
            except FileNotFoundError as e:
                print(f"dashboard/index.html не найден: {str(e)}")
                # Попробуем создать папку и файл автоматически
                try:
                    os.makedirs("static/dashboard", exist_ok=True)
                    self.send_response(404)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"404 - Dashboard files missing. Directory created, please add necessary files.")
                except Exception as dir_error:
                    print(f"Ошибка создания директории: {str(dir_error)}")
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(f"500 - Server error: {str(dir_error)}".encode())
            except Exception as e:
                print(f"Ошибка при обработке /dashboard: {str(e)}")
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"500 - Server error: {str(e)}".encode())
        
        elif self.path.startswith('/dashboard/'):
            # Обработка файлов дашборда
            file_path = os.path.join("static", self.path[1:])
            print(f"Запрос файла дашборда: {file_path}")
            
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    self.send_response(200)
                    
                    # Установка правильного типа содержимого
                    if file_path.endswith('.jsx'):
                        self.send_header("Content-type", "text/babel")
                    elif file_path.endswith('.js'):
                        self.send_header("Content-type", "application/javascript")
                    elif file_path.endswith('.css'):
                        self.send_header("Content-type", "text/css")
                    elif file_path.endswith('.json'):
                        self.send_header("Content-type", "application/json")
                    elif file_path.endswith('.html'):
                        self.send_header("Content-type", "text/html")
                    else:
                        self.send_header("Content-type", "text/plain")
                    
                    self.end_headers()
                    self.wfile.write(content)
                    print(f"Файл {file_path} успешно отправлен ({len(content)} байт)")
            
            except FileNotFoundError:
                print(f"Файл не найден: {file_path}")
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"404 - File not found: {file_path}".encode())
            
            except Exception as e:
                print(f"Ошибка при обработке {file_path}: {str(e)}")
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"500 - Server error: {str(e)}".encode())
        
        elif self.path == '/api/rfm-data':
            # API для получения данных RFM-анализа
            print("Запрос API: /api/rfm-data")
            self.handle_rfm_data_api()
        
        elif self.path == '/api/upload-history':
            # API для получения истории загрузок
            print("Запрос API: /api/upload-history")
            self.handle_upload_history_api()
        
        else:
            print(f"GET {self.path} not found")
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 - Not Found")

    def handle_rfm_data_api(self):
        """Обработчик API для получения данных RFM-анализа"""
        # Получаем последний файл результатов
        results_dir = "results"
        if os.path.exists(results_dir):
            files = sorted(
                [f for f in os.listdir(results_dir) if f.startswith('rfm_results_')],
                key=lambda x: os.path.getmtime(os.path.join(results_dir, x)),
                reverse=True
            )
            
            if files:
                latest_file = os.path.join(results_dir, files[0])
                try:
                    # Читаем CSV файл
                    rfm_df = pd.read_csv(latest_file)
                    
                    # Преобразуем в формат JSON
                    rfm_data = {
                        "customers": rfm_df.to_dict(orient='records'),
                        "summary": {
                            "total_customers": int(rfm_df[rfm_df.columns[0]].nunique()),
                            "total_revenue": float(rfm_df['Monetary'].sum()),
                            "avg_recency": float(rfm_df['Recency'].mean()),
                            "avg_frequency": float(rfm_df['Frequency'].mean()),
                            "avg_monetary": float(rfm_df['Monetary_Mean'].mean())
                        },
                        "segments": rfm_df.groupby('Customer_Segment').size().to_dict(),
                        "rfm_scores": rfm_df.groupby('RFM_Score').size().to_dict()
                    }
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(rfm_data).encode())
                    return
                except Exception as e:
                    print(f"Error processing RFM data: {str(e)}")
                    traceback.print_exc()
        
        self.send_response(404)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "No RFM data found"}).encode())

    def handle_upload_history_api(self):
        """Обработчик API для получения истории загрузок"""
        results_dir = "results"
        if os.path.exists(results_dir):
            try:
                # Получаем список файлов с результатами
                files = [f for f in os.listdir(results_dir) if f.startswith('rfm_results_')]
                upload_history = []
                
                for i, filename in enumerate(files):
                    timestamp = filename.split('_')[-1].split('.')[0]
                    date_str = datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y')
                    
                    # Читаем краткую информацию из файла
                    file_path = os.path.join(results_dir, filename)
                    try:
                        rfm_df = pd.read_csv(file_path)
                        segment_count = rfm_df['Customer_Segment'].nunique()
                        record_count = len(rfm_df)
                        
                        upload_history.append({
                            "id": i + 1,
                            "filename": filename,
                            "date": date_str,
                            "records": record_count,
                            "segments": segment_count
                        })
                    except Exception as e:
                        print(f"Ошибка при чтении файла {filename}: {str(e)}")
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(upload_history).encode())
                return
            except Exception as e:
                print(f"Ошибка при получении истории загрузок: {str(e)}")
                traceback.print_exc()
        
        # В случае ошибки или отсутствия файлов возвращаем пустой список
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps([]).encode())

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')

            if self.path == '/register':
                if not firebase_admin_imported:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Firebase не настроен"}).encode())
                    return
                    
                data = dict(x.split('=') for x in post_data.decode('utf-8').split('&'))
                email = unquote(data.get('email'))
                password = unquote(data.get('password'))
                print(f"Registering user: {email}")
                
                try:
                    user = auth.create_user(email=email, password=password)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "Регистрация прошла успешно"}).encode())
                except Exception as e:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": f"Ошибка регистрации: {str(e)}"}).encode())

            elif self.path == '/login':
                if not firebase_admin_imported:
                    # Упрощенная авторизация для случая, когда Firebase не настроен
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("X-Auth-Token", "demo-token")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "Демо-режим: вход без Firebase"}).encode())
                    return
                    
                data = dict(x.split('=') for x in post_data.decode('utf-8').split('&'))
                email = unquote(data.get('email'))
                password = unquote(data.get('password'))
                print(f"Logging in user: {email}")
                
                try:
                    user = auth.get_user_by_email(email)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("X-Auth-Token", user.uid)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "Вход успешен"}).encode())
                except Exception as e:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": f"Ошибка входа: {str(e)}"}).encode())

            elif self.path == '/upload':
                auth_token = self.headers.get('Authorization', '')
                if firebase_admin_imported and not self.check_auth(auth_token):
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Требуется авторизация"}).encode())
                    return
                
                # Исправленный парсинг multipart/form-data
                if 'multipart/form-data' in content_type:
                    # Извлекаем boundary, обрабатываем кавычки
                    boundary = content_type.split('boundary=')[1]
                    if boundary.startswith('"') and boundary.endswith('"'):
                        boundary = boundary[1:-1]
                    boundary = boundary.encode()
                    
                    # Правильный разбор многокомпонентных данных формы
                    parts = post_data.split(b'--' + boundary)
                    file_data = None
                    customer_col, date_col, amount_col = None, None, None
                    
                    for part in parts:
                        if b'Content-Disposition: form-data' not in part:
                            continue
                            
                        # Извлекаем имя поля формы
                        header_end = part.find(b'\r\n\r\n')
                        if header_end == -1:
                            continue
                            
                        headers = part[:header_end].decode('utf-8', errors='ignore')
                        body = part[header_end + 4:]
                        
                        # Удаляем трейлер в конце, если есть
                        if body.endswith(b'\r\n'):
                            body = body[:-2]
                        
                        if 'name="file"' in headers:
                            file_data = body
                        elif 'name="customer_col"' in headers:
                            customer_col = body.decode('utf-8', errors='ignore').strip()
                            print(f"Selected customer_col: {customer_col}")
                        elif 'name="date_col"' in headers:
                            date_col = body.decode('utf-8', errors='ignore').strip()
                            print(f"Selected date_col: {date_col}")
                        elif 'name="amount_col"' in headers:
                            amount_col = body.decode('utf-8', errors='ignore').strip()
                            print(f"Selected amount_col: {amount_col}")
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Неверный формат данных"}).encode())
                    return

                if not file_data or not customer_col or not date_col or not amount_col:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Не указаны все необходимые данные"}).encode())
                    return
                
                # Сохраняем файл
                file_name = f"upload_{int(datetime.now().timestamp())}.csv"
                with open(file_name, "wb") as f:
                    f.write(file_data)
                
                print(f"Сохранён файл {file_name} размером {len(file_data)} байт")
                
                # Пытаемся прочитать файл с разными кодировками
                try:
                    data = pd.read_csv(file_name, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        data = pd.read_csv(file_name, encoding='latin-1')
                    except Exception as e:
                        print(f"Ошибка при чтении CSV: {str(e)}")
                        self.send_response(400)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "error", "message": f"Ошибка при чтении CSV: {str(e)}"}).encode())
                        return
                
                print(f"Колонки в CSV: {list(data.columns)}")
                
                # Проверяем наличие необходимых колонок
                required_cols = {customer_col, date_col, amount_col}
                actual_cols = set(data.columns)
                print(f"Требуемые колонки: {required_cols}")
                print(f"Колонки в данных: {actual_cols}")
                
                if not required_cols.issubset(actual_cols):
                    missing = required_cols - actual_cols
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": f"Отсутствуют колонки: {', '.join(missing)}"}).encode())
                    return
                
                # Дополнительная диагностика
                print(f"Первые 5 строк данных:\n{data.head()}")
                
                try:
                    rfm_df, additional_info = rfm_analysis(data, date_col, customer_col, amount_col)
                    rfm_result = {
                        "total_customers": int(rfm_df[customer_col].nunique()),
                        "total_revenue": float(rfm_df['Monetary'].sum()),
                        "segments": additional_info['segment_distribution'].set_index('Customer_Segment')['Count'].to_dict()
                    }
                    
                    # Сохранение результатов в Firebase только если Firebase настроен
                    if firebase_admin_imported:
                        try:
                            # Пробуем сохранить в Firebase Storage
                            try:
                                blob = bucket.blob(f"uploads/{file_name}")
                                with open(file_name, "rb") as f:
                                    blob.upload_from_file(f, content_type="text/csv")
                                print(f"Файл успешно загружен в Firebase Storage")
                            except Exception as storage_error:
                                print(f"Ошибка при загрузке в Firebase Storage: {str(storage_error)}")
                            
                            # Пробуем сохранить в Firestore
                            try:
                                db.collection("rfm_results").add({
                                    "file_name": file_name,
                                    "result": rfm_result,
                                    "timestamp": firestore.SERVER_TIMESTAMP
                                })
                                print(f"Результаты успешно сохранены в Firestore")
                            except Exception as firestore_error:
                                print(f"Ошибка при сохранении в Firestore: {str(firestore_error)}")
                        except Exception as firebase_error:
                            print(f"Общая ошибка при работе с Firebase: {str(firebase_error)}")
                    else:
                        print("Firebase не инициализирован, результаты не сохранены в облаке")
                    
                    # Создаем директорию results, если её нет
                    results_dir = "results"
                    if not os.path.exists(results_dir):
                        os.makedirs(results_dir)
                    
                    # Сохраняем локально в CSV-файл
                    result_file = f"{results_dir}/rfm_results_{int(datetime.now().timestamp())}.csv"
                    rfm_df.to_csv(result_file, index=False)
                    print(f"Результаты сохранены в {result_file}")
                    
                    # Обновляем исходную страницу index.html, чтобы добавить ссылку на дашборд
                    try:
                        self.ensure_dashboard_link_in_index()
                    except Exception as e:
                        print(f"Не удалось добавить ссылку на дашборд: {str(e)}")

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(rfm_result).encode())
                except Exception as e:
                    print(f"Ошибка в функции rfm_analysis: {str(e)}")
                    traceback.print_exc()  # Печатаем полный стек ошибки
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())

        except Exception as e:
            print(f"Общая ошибка: {str(e)}")
            traceback.print_exc()  # Печатаем полный стек ошибки
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())

    def ensure_dashboard_link_in_index(self):
        """Убеждаемся, что в index.html есть ссылка на дашборд"""
        index_path = "static/index.html"
        
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Проверяем, есть ли ссылка на дашборд
            if '<a href="/dashboard"' not in content and 'id="results-card"' in content:
                # Добавляем ссылку на дашборд
                dashboard_link = '\n<div class="text-center mt-4">\n<a href="/dashboard" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Открыть расширенный дашборд</a>\n</div>\n'
                
                # Находим место для вставки ссылки
                results_end_pos = content.find('</div>', content.find('id="results-card"'))
                if results_end_pos != -1:
                    new_content = content[:results_end_pos] + dashboard_link + content[results_end_pos:]
                    
                    # Сохраняем обновленный файл
                    with open(index_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                        
                    print("Ссылка на дашборд добавлена в index.html")
        except Exception as e:
            print(f"Ошибка при обновлении index.html: {str(e)}")
            # Не останавливаем основной процесс из-за ошибки
            pass

    def check_auth(self, auth_header):
        if not firebase_admin_imported:
            return True  # В режиме без Firebase авторизация всегда успешна
            
        try:
            user = auth.get_user(auth_header)
            return True
        except:
            return False

# Создаем и запускаем сервер
Handler = SimpleHTTPRequestHandler

# Проверяем наличие директории dashboard и создаем её при необходимости
try:
    os.makedirs("static/dashboard", exist_ok=True)
    print("Директория 'static/dashboard' проверена/создана")
except Exception as e:
    print(f"Ошибка при создании директории static/dashboard: {str(e)}")

try:
    print(f"Запуск сервера на http://localhost:{PORT}")
    httpd = socketserver.TCPServer(("", PORT), Handler)
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Сервер остановлен пользователем")
except Exception as e:
    print(f"Ошибка при запуске сервера: {str(e)}")