import http.server
import socketserver
import pandas as pd
from rfmpro_analysis import rfm_analysis
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
from urllib.parse import unquote  # Добавляем для декодирования URL

PORT = 8000

# Инициализация Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred, {"storageBucket": "rfmpro-ed06f.appspot.com"})
db = firestore.client()
bucket = storage.bucket()

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
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
        else:
            print(f"GET {self.path} not found")
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')

            if self.path == '/register':
                # Декодируем данные формы и обрабатываем URL-кодировку
                data = dict(x.split('=') for x in post_data.decode('utf-8').split('&'))
                email = unquote(data.get('email'))  # Декодируем email (например, %40 → @)
                password = unquote(data.get('password'))  # Декодируем пароль
                print(f"Registering user: {email}")
                user = auth.create_user(email=email, password=password)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Регистрация прошла успешно"}).encode())

            elif self.path == '/login':
                data = dict(x.split('=') for x in post_data.decode('utf-8').split('&'))
                email = unquote(data.get('email'))
                password = unquote(data.get('password'))
                print(f"Logging in user: {email}")
                user = auth.get_user_by_email(email)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("X-Auth-Token", user.uid)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Вход успешен"}).encode())

            elif self.path == '/upload':
                auth_token = self.headers.get('Authorization', '')
                if not auth_token or not self.check_auth(auth_token):
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Требуется авторизация"}).encode())
                    return
                
                boundary = content_type.split('boundary=')[1].encode()
                parts = post_data.split(b'--' + boundary)
                file_data = None
                customer_col, date_col, amount_col = None, None, None
                
                for part in parts:
                    if b'Content-Disposition: form-data' in part:
                        if b'name="file"' in part:
                            file_start = part.index(b'\r\n\r\n') + 4
                            file_end = part.rindex(b'\r\n--')
                            file_data = part[file_start:file_end]
                        elif b'name="customer_col"' in part:
                            customer_col = part.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode('utf-8')
                        elif b'name="date_col"' in part:
                            date_col = part.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode('utf-8')
                        elif b'name="amount_col"' in part:
                            amount_col = part.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode('utf-8')

                if not file_data or not customer_col or not date_col or not amount_col:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Не указаны все данные"}).encode())
                    return
                
                file_name = f"upload_{int(datetime.now().timestamp())}.csv"
                with open(file_name, "wb") as f:
                    f.write(file_data)
                
                print(f"Сохранён файл {file_name} размером {len(file_data)} байт")
                data = pd.read_csv(file_name)
                print(f"Колонки в CSV: {data.columns.tolist()}")
                
                if not {customer_col, date_col, amount_col}.issubset(data.columns):
                    missing = {customer_col, date_col, amount_col} - set(data.columns)
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": f"Отсутствуют колонки: {missing}"}).encode())
                    return
                
                rfm_df, additional_info = rfm_analysis(data, date_col, customer_col, amount_col)
                rfm_result = {
                    "total_customers": int(rfm_df[customer_col].nunique()),
                    "total_revenue": float(rfm_df['Monetary'].sum()),
                    "segments": additional_info['segment_distribution'].set_index('Customer_Segment')['Count'].to_dict()
                }
                
                blob = bucket.blob(f"uploads/{file_name}")
                with open(file_name, "rb") as f:
                    blob.upload_from_file(f, content_type="text/csv")
                
                db.collection("rfm_results").add({
                    "file_name": file_name,
                    "result": rfm_result,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(rfm_result).encode())

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())

    def check_auth(self, auth_header):
        try:
            user = auth.get_user(auth_header)
            return True
        except:
            return False

Handler = SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Сервер запущен на http://localhost:{PORT}")
    httpd.serve_forever()