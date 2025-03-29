import http.server
import socketserver
import pandas as pd
from supabase import create_client
from rfm_analysis import perform_rfm_analysis
import os
from dotenv import load_dotenv
import base64
import json
import logging
from datetime import datetime
import urllib.parse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    logger.error("Отсутствуют переменные окружения SUPABASE_URL и/или SUPABASE_KEY")
    exit(1)

# Инициализация клиента Supabase
try:
    supabase = create_client(supabase_url, supabase_key)
    logger.info("Соединение с Supabase установлено успешно")
except Exception as e:
    logger.error(f"Ошибка соединения с Supabase: {str(e)}")
    exit(1)

PORT = 8000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        """Переопределение метода логирования для использования модуля logging"""
        logger.info("%s - %s" % (self.address_string(), format % args))

    def do_GET(self):
        """Обработка GET-запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                with open("static/index.html", "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                logger.error("Файл static/index.html не найден")
                self.send_error(500, "Файл не найден")
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            try:
                with open("static/style.css", "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                logger.error("Файл static/style.css не найден")
                self.send_error(500, "Файл не найден")
        else:
            self.send_response(404)
            self.end_headers()

    def send_json_response(self, status_code, data):
        """Вспомогательный метод для отправки JSON-ответов"""
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def parse_form_data(self, post_data, content_type):
        """Разбор формы в зависимости от типа контента"""
        if 'application/x-www-form-urlencoded' in content_type:
            return dict(urllib.parse.parse_qsl(post_data.decode('utf-8')))
        elif 'multipart/form-data' in content_type:
            boundary = content_type.split('boundary=')[1].encode()
            parts = post_data.split(b'--' + boundary)
            form_data = {}
            file_data = None
            
            for part in parts:
                if b'Content-Disposition: form-data' in part:
                    lines = part.split(b'\r\n')
                    disposition = next((line for line in lines if b'Content-Disposition' in line), b'')
                    
                    # Извлечение имени поля
                    name_match = None
                    if b'name="' in disposition:
                        name_start = disposition.find(b'name="') + 6
                        name_end = disposition.find(b'"', name_start)
                        name = disposition[name_start:name_end].decode('utf-8')
                    else:
                        continue
                    
                    # Проверка на файл
                    if b'filename="' in disposition:
                        # Извлекаем содержимое файла
                        file_start = part.find(b'\r\n\r\n') + 4
                        file_end = part.rfind(b'\r\n--')
                        if file_end > file_start:
                            file_data = part[file_start:file_end]
                            form_data[name] = file_data
                    else:
                        # Извлекаем обычное поле формы
                        content_start = part.find(b'\r\n\r\n') + 4
                        content_end = part.rfind(b'\r\n--')
                        if content_end > content_start:
                            form_data[name] = part[content_start:content_end].decode('utf-8').strip()
            
            return form_data, file_data
        
        return None, None

    def do_POST(self):
        """Обработка POST-запросов"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            
            # Обработка запроса регистрации
            if self.path == '/register':
                if 'application/x-www-form-urlencoded' in content_type:
                    data = dict(urllib.parse.parse_qsl(post_data.decode('utf-8')))
                    email = data.get('email')
                    password = data.get('password')
                    
                    if not email or not password:
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": "Отсутствуют email или password"
                        })
                        return
                    
                    # Проверка наличия пользователя
                    existing_user = supabase.table('users').select('*').eq('email', email).execute()
                    if existing_user.data and len(existing_user.data) > 0:
                        self.send_json_response(409, {
                            "status": "error", 
                            "message": "Пользователь с таким email уже существует"
                        })
                        return
                    
                    # Хеширование пароля должно быть добавлено здесь в реальном приложении
                    try:
                        supabase.table('users').insert({'email': email, 'password': password}).execute()
                        self.send_json_response(200, {
                            "status": "success", 
                            "message": "Регистрация прошла успешно"
                        })
                    except Exception as e:
                        logger.error(f"Ошибка регистрации: {str(e)}")
                        self.send_json_response(500, {
                            "status": "error", 
                            "message": "Ошибка при регистрации пользователя"
                        })
                else:
                    self.send_json_response(415, {
                        "status": "error", 
                        "message": "Неподдерживаемый тип контента"
                    })
            
            # Обработка запроса входа
            elif self.path == '/login':
                if 'application/x-www-form-urlencoded' in content_type:
                    data = dict(urllib.parse.parse_qsl(post_data.decode('utf-8')))
                    email = data.get('email')
                    password = data.get('password')
                    
                    if not email or not password:
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": "Отсутствуют email или password"
                        })
                        return
                    
                    try:
                        # В реальном приложении здесь должна быть проверка хешированного пароля
                        user = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
                        
                        if user.data and len(user.data) > 0:
                            auth = base64.b64encode(f"{email}:{password}".encode()).decode()
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.send_header("X-Auth-Token", auth)
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                "status": "success", 
                                "message": "Вход успешен"
                            }).encode())
                        else:
                            self.send_json_response(401, {
                                "status": "error", 
                                "message": "Неверные данные для входа"
                            })
                    except Exception as e:
                        logger.error(f"Ошибка входа: {str(e)}")
                        self.send_json_response(500, {
                            "status": "error", 
                            "message": "Ошибка при входе в систему"
                        })
                else:
                    self.send_json_response(415, {
                        "status": "error", 
                        "message": "Неподдерживаемый тип контента"
                    })
            
            # Обработка запроса загрузки файла
            elif self.path == '/upload':
                # Проверка авторизации
                auth = self.headers.get('Authorization', '')
                if not auth or not self.check_auth(auth):
                    self.send_json_response(401, {
                        "status": "error", 
                        "message": "Требуется авторизация"
                    })
                    return
                
                # Принимаем как multipart/form-data, так и application/json
                if 'multipart/form-data' in content_type:
                    form_data, file_data = self.parse_form_data(post_data, content_type)
                    
                    customer_col = form_data.get('customer_col')
                    date_col = form_data.get('date_col')
                    amount_col = form_data.get('amount_col')
                elif 'application/json' in content_type:
                    try:
                        json_data = json.loads(post_data.decode('utf-8'))
                        file_data = None
                        
                        # Проверяем, есть ли base64-данные файла
                        if 'file_data' in json_data and json_data['file_data']:
                            try:
                                file_data = base64.b64decode(json_data['file_data'])
                            except Exception as e:
                                logger.error(f"Ошибка декодирования base64-данных: {str(e)}")
                        
                        customer_col = json_data.get('customer_col', 'customer_id')  # Значения по умолчанию
                        date_col = json_data.get('date_col', 'date')
                        amount_col = json_data.get('amount_col', 'amount')
                    except json.JSONDecodeError as e:
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": f"Некорректный JSON: {str(e)}"
                        })
                        return
                else:
                    self.send_json_response(415, {
                        "status": "error", 
                        "message": "Поддерживаются типы контента: multipart/form-data или application/json"
                    })
                    return
                
                # Если не указаны поля, используем значения по умолчанию
                if not customer_col:
                    customer_col = 'customer_id'
                    logger.info("Используется колонка клиента по умолчанию: customer_id")
                
                if not date_col:
                    date_col = 'date'
                    logger.info("Используется колонка даты по умолчанию: date")
                
                if not amount_col:
                    amount_col = 'amount'
                    logger.info("Используется колонка суммы по умолчанию: amount")
                
                if not file_data:
                    self.send_json_response(400, {
                        "status": "error", 
                        "message": "Отсутствует файл с данными"
                    })
                    return
                
                # Сохранение файла
                temp_file_path = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                try:
                    with open(temp_file_path, "wb") as f:
                        f.write(file_data)
                    
                    logger.info(f"Сохранён файл {temp_file_path} размером {len(file_data)} байт")
                    
                    # Чтение CSV с явными параметрами
                    try:
                        data = pd.read_csv(
                            temp_file_path, 
                            sep=',',  # Явно указываем разделитель
                            encoding='utf-8',  # Указываем кодировку
                            quotechar='"',  # Символ кавычек для текстовых значений
                            escapechar='\\',  # Escape-символ
                            low_memory=False  # Отключаем режим экономии памяти для больших файлов
                        )
                        logger.info(f"Колонки в CSV: {data.columns.tolist()}")
                    except Exception as e:
                        logger.error(f"Ошибка чтения CSV: {str(e)}")
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": f"Ошибка чтения CSV: {str(e)}"
                        })
                        return
                    
                    # Предварительная обработка названий столбцов
                    # Приводим все названия столбцов к нижнему регистру и удаляем лишние пробелы
                    data.columns = [col.strip().lower() for col in data.columns]
                    
                    # Приводим искомые названия колонок к тому же формату
                    customer_col_norm = customer_col.strip().lower()
                    date_col_norm = date_col.strip().lower()
                    amount_col_norm = amount_col.strip().lower()
                    
                    # Словари возможных альтернативных названий для каждого типа колонок
                    customer_alternatives = ['customer', 'client', 'customer_id', 'client_id', 'customerid', 'clientid', 'user', 'user_id', 'userid', 'клиент', 'id клиента', 'покупатель', 'пользователь']
                    date_alternatives = ['date', 'datetime', 'time', 'purchase_date', 'transaction_date', 'order_date', 'дата', 'дата покупки', 'дата заказа', 'дата транзакции']
                    amount_alternatives = ['amount', 'sum', 'price', 'total', 'value', 'transaction_amount', 'revenue', 'сумма', 'стоимость', 'сумма покупки', 'цена']
                    
                    # Функция для поиска подходящей колонки
                    def find_matching_column(target_col, alternatives, columns):
                        # Сначала проверяем точное совпадение
                        if target_col in columns:
                            return target_col
                        
                        # Затем проверяем альтернативные варианты
                        for alt in alternatives:
                            if alt in columns:
                                logger.info(f"Найдена альтернативная колонка '{alt}' вместо '{target_col}'")
                                return alt
                        
                        # Ищем по частичному совпадению
                        for col in columns:
                            for alt in alternatives:
                                if alt in col or col in alt:
                                    logger.info(f"Найдено частичное совпадение колонки '{col}' для '{target_col}'")
                                    return col
                        
                        return None
                    
                    # Определяем фактические колонки
                    actual_customer_col = find_matching_column(customer_col_norm, customer_alternatives, data.columns)
                    actual_date_col = find_matching_column(date_col_norm, date_alternatives, data.columns)
                    actual_amount_col = find_matching_column(amount_col_norm, amount_alternatives, data.columns)
                    
                    # Проверка наличия всех необходимых колонок
                    missing_cols = []
                    if not actual_customer_col:
                        missing_cols.append(f"колонка клиента (указана как '{customer_col}')")
                    if not actual_date_col:
                        missing_cols.append(f"колонка даты (указана как '{date_col}')")
                    if not actual_amount_col:
                        missing_cols.append(f"колонка суммы (указана как '{amount_col}')")
                    
                    if missing_cols:
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": f"Не удалось найти следующие колонки: {', '.join(missing_cols)}"
                        })
                        os.remove(temp_file_path)  # Удаляем временный файл
                        return
                        
                    # Переименовываем найденные колонки для работы rfm_analysis
                    column_mapping = {}
                    if actual_customer_col != customer_col:
                        column_mapping[actual_customer_col] = customer_col
                    if actual_date_col != date_col:
                        column_mapping[actual_date_col] = date_col
                    if actual_amount_col != amount_col:
                        column_mapping[actual_amount_col] = amount_col
                    
                    if column_mapping:
                        data = data.rename(columns=column_mapping)
                        logger.info(f"Переименованы колонки: {column_mapping}")
                    
                    # Выполнение RFM-анализа
                    try:
                        # Выводим информацию о колонках, которые будут использоваться
                        logger.info(f"Выполнение RFM-анализа с колонками: customer={customer_col}, date={date_col}, amount={amount_col}")
                        # Проверяем типы данных
                        logger.info(f"Типы данных: {data.dtypes}")
                        
                        # Преобразование даты, если это строка
                        if pd.api.types.is_string_dtype(data[date_col]):
                            try:
                                # Пробуем несколько форматов даты
                                formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', 
                                          '%d-%m-%Y', '%m-%d-%Y', '%Y.%m.%d', '%d.%m.%y', '%d/%m/%y']
                                for format_str in formats:
                                    try:
                                        data[date_col] = pd.to_datetime(data[date_col], format=format_str)
                                        logger.info(f"Успешно преобразована дата с форматом {format_str}")
                                        break
                                    except:
                                        continue
                                else:
                                    # Если не сработал ни один формат, пробуем автоматическое определение
                                    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                                    logger.info("Использовано автоматическое определение формата даты")
                            except Exception as e:
                                logger.warning(f"Ошибка преобразования даты: {str(e)}")
                        
                        # Преобразование суммы, если это строка
                        if pd.api.types.is_string_dtype(data[amount_col]):
                            # Заменяем запятые на точки, удаляем пробелы, валютные символы и др.
                            data[amount_col] = data[amount_col].str.replace(',', '.').str.replace(' ', '')
                            data[amount_col] = data[amount_col].str.replace(r'[^\d.]', '', regex=True)
                            data[amount_col] = pd.to_numeric(data[amount_col], errors='coerce')
                            logger.info("Выполнено преобразование столбца суммы в числовой формат")
                        
                        # Проверяем, есть ли пропущенные значения после преобразования
                        missing_count = data[[customer_col, date_col, amount_col]].isna().sum()
                        logger.info(f"Пропущенные значения после преобразования: {missing_count.to_dict()}")
                        
                        # Удаляем строки с пропущенными значениями в ключевых колонках
                        original_rows = len(data)
                        data = data.dropna(subset=[customer_col, date_col, amount_col])
                        logger.info(f"Удалено {original_rows - len(data)} строк с пропущенными значениями")
                        
                        rfm_result = perform_rfm_analysis(data, customer_col, date_col, amount_col)
                        
                        # Сохранение результатов
                        storage_file_name = f"result_{int(datetime.now().timestamp())}.csv"
                        
                        # Загрузка в Supabase
                        try:
                            with open(temp_file_path, 'rb') as f:
                                supabase.storage.from_('uploads').upload(storage_file_name, f)
                            
                            # Сохранение результатов анализа
                            supabase.table('rfm_results').insert({
                                'file_name': storage_file_name, 
                                'result': json.dumps(rfm_result)
                            }).execute()
                            
                            self.send_json_response(200, rfm_result)
                        except Exception as e:
                            logger.error(f"Ошибка сохранения результатов: {str(e)}")
                            self.send_json_response(500, {
                                "status": "error", 
                                "message": f"Ошибка сохранения результатов: {str(e)}"
                            })
                    except Exception as e:
                        logger.error(f"Ошибка при выполнении RFM-анализа: {str(e)}")
                        self.send_json_response(500, {
                            "status": "error", 
                            "message": f"Ошибка при выполнении RFM-анализа: {str(e)}"
                        })
                except Exception as e:
                    logger.error(f"Ошибка обработки файла: {str(e)}")
                    self.send_json_response(500, {
                        "status": "error", 
                        "message": f"Ошибка обработки файла: {str(e)}"
                    })
                finally:
                    # Удаляем временный файл, если он существует
                    if os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                            logger.info(f"Удален временный файл {temp_file_path}")
                        except Exception as e:
                            logger.error(f"Ошибка удаления временного файла: {str(e)}")
            else:
                self.send_response(404)
                self.end_headers()

        except Exception as e:
            logger.error(f"Необработанная ошибка: {str(e)}")
            self.send_json_response(500, {
                "status": "error", 
                "message": f"Внутренняя ошибка сервера: {str(e)}"
            })

    def check_auth(self, auth_header):
        """Проверка аутентификации пользователя"""
        try:
            if not auth_header.startswith('Basic '):
                return False
            
            encoded = auth_header.split(' ')[1]
            decoded = base64.b64decode(encoded).decode('utf-8')
            
            if ':' not in decoded:
                return False
                
            email, password = decoded.split(':', 1)
            
            # В реальном приложении здесь должна быть проверка хешированного пароля
            user = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
            return user.data and len(user.data) > 0
        except Exception as e:
            logger.error(f"Ошибка проверки аутентификации: {str(e)}")
            return False


def run_server():
    """Запуск сервера"""
    try:
        Handler = SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            logger.info(f"Сервер запущен на http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен")
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {str(e)}")


if __name__ == "__main__":
    run_server()