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
import re
from datetime import datetime
import urllib.parse
import io

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
        logger.info(f"Парсинг данных с Content-Type: {content_type}")
        
        if 'application/x-www-form-urlencoded' in content_type:
            return dict(urllib.parse.parse_qsl(post_data.decode('utf-8'))), None
        elif 'multipart/form-data' in content_type:
            try:
                boundary = content_type.split('boundary=')[1].encode()
                logger.info(f"Обнаружена граница: {boundary}")
                parts = post_data.split(b'--' + boundary)
                logger.info(f"Разделено {len(parts)} частей")
                
                form_data = {}
                file_data = None
                
                for i, part in enumerate(parts):
                    if i == 0 or i == len(parts) - 1:  # Пропускаем первую и последнюю "пустые" части
                        continue
                        
                    if b'Content-Disposition: form-data' in part:
                        # Ищем имя поля
                        disposition_line = next((line for line in part.split(b'\r\n') if b'Content-Disposition' in line), None)
                        if not disposition_line:
                            continue
                            
                        logger.info(f"Анализ части {i}: {disposition_line}")
                        
                        # Получаем имя поля
                        name_match = re.search(b'name="([^"]*)"', disposition_line)
                        if not name_match:
                            continue
                            
                        field_name = name_match.group(1).decode('utf-8')
                        logger.info(f"Обнаружено поле: {field_name}")
                        
                        # Проверяем, файл ли это
                        is_file = b'filename="' in disposition_line
                        
                        # Ищем начало и конец содержимого
                        content_start = part.find(b'\r\n\r\n')
                        if content_start == -1:
                            continue
                            
                        content_start += 4  # длина '\r\n\r\n'
                        content = part[content_start:]
                        
                        # Удаляем концевые \r\n
                        if content.endswith(b'\r\n'):
                            content = content[:-2]
                        
                        if is_file:
                            logger.info(f"Обнаружены данные файла в поле {field_name}, размер: {len(content)} байт")
                            file_data = content
                            form_data[field_name] = "FILE_DATA_PRESENT"  # Метка наличия файла
                        else:
                            try:
                                value = content.decode('utf-8')
                                form_data[field_name] = value
                                logger.info(f"Поле {field_name} = {value}")
                            except UnicodeDecodeError:
                                logger.warning(f"Не удалось декодировать содержимое поля {field_name}")
                
                logger.info(f"Извлечено полей: {len(form_data)}, наличие файла: {file_data is not None}")
                return form_data, file_data
            except Exception as e:
                logger.error(f"Ошибка при разборе multipart/form-data: {str(e)}")
                return {}, None
        elif 'application/json' in content_type:
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                logger.info(f"Получены JSON-данные: {list(json_data.keys())}")
                
                file_data = None
                if 'file_data' in json_data:
                    try:
                        file_data = base64.b64decode(json_data['file_data'])
                        logger.info(f"Декодированы base64-данные файла, размер: {len(file_data)} байт")
                        # Удаляем из JSON чтобы не дублировать в логах
                        json_data_for_log = dict(json_data)
                        json_data_for_log['file_data'] = f"BASE64_DATA ({len(json_data['file_data'])} символов)"
                        logger.info(f"JSON-данные: {json_data_for_log}")
                    except Exception as e:
                        logger.error(f"Ошибка декодирования base64-данных: {str(e)}")
                
                return json_data, file_data
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка декодирования JSON: {str(e)}")
                return {}, None
        
        logger.warning(f"Неподдерживаемый тип контента: {content_type}")
        return {}, None

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
                if 'multipart/form-data' in content_type or 'application/json' in content_type:
                    form_data, file_data = self.parse_form_data(post_data, content_type)
                    
                    # Определяем названия колонок из запроса
                    customer_col = form_data.get('customer_col')
                    date_col = form_data.get('date_col')
                    amount_col = form_data.get('amount_col')
                    
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
                    
                    # Проверяем наличие файла
                    if not file_data:
                        # Проверяем, был ли загружен файл через field с именем 'file'
                        if isinstance(form_data.get('file'), bytes):
                            file_data = form_data.get('file')
                            logger.info(f"Файл найден в поле 'file', размер: {len(file_data)} байт")
                    
                    if not file_data:
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": "Отсутствует файл с данными. Убедитесь, что вы отправляете файл в поле 'file' или в формате base64 в поле 'file_data'"
                        })
                        return
                    
                    # Логируем информацию для отладки
                    logger.info(f"Получены данные: customer_col={customer_col}, date_col={date_col}, amount_col={amount_col}")
                    logger.info(f"Размер файла данных: {len(file_data)} байт")
                else:
                    self.send_json_response(415, {
                        "status": "error", 
                        "message": "Поддерживаются типы контента: multipart/form-data или application/json"
                    })
                
                # Сохранение файла
                temp_file_path = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                try:
                    with open(temp_file_path, "wb") as f:
                        f.write(file_data)
                    
                    logger.info(f"Сохранён файл {temp_file_path} размером {len(file_data)} байт")
                    
                    # Пробуем разные способы чтения файла
                    read_methods = [
                        # Стандартный способ
                        lambda: pd.read_csv(
                            temp_file_path, 
                            sep=',',
                            encoding='utf-8',
                            quotechar='"',
                            escapechar='\\',
                            low_memory=False
                        ),
                        # С другим разделителем
                        lambda: pd.read_csv(
                            temp_file_path, 
                            sep=';',
                            encoding='utf-8',
                            quotechar='"',
                            escapechar='\\',
                            low_memory=False
                        ),
                        # С другой кодировкой
                        lambda: pd.read_csv(
                            temp_file_path, 
                            sep=',',
                            encoding='latin1',
                            quotechar='"',
                            escapechar='\\',
                            low_memory=False
                        ),
                        # Прямо из памяти
                        lambda: pd.read_csv(
                            io.BytesIO(file_data), 
                            sep=',',
                            encoding='utf-8',
                            quotechar='"',
                            escapechar='\\',
                            low_memory=False
                        ),
                        # Еще одна попытка с другой кодировкой и разделителем
                        lambda: pd.read_csv(
                            io.BytesIO(file_data), 
                            sep=';',
                            encoding='latin1',
                            quotechar='"',
                            escapechar='\\',
                            low_memory=False
                        )
                    ]
                    
                    data = None
                    last_error = None
                    
                    for i, read_method in enumerate(read_methods):
                        try:
                            logger.info(f"Попытка чтения CSV методом #{i+1}")
                            data = read_method()
                            
                            # Проверяем, успешно ли прочитаны данные
                            if len(data.columns) <= 1:
                                logger.warning(f"Метод #{i+1}: найдена только одна колонка, возможно, неверный разделитель")
                                continue
                                
                            logger.info(f"Успешное чтение CSV методом #{i+1}, обнаружено колонок: {len(data.columns)}")
                            logger.info(f"Колонки: {data.columns.tolist()}")
                            break
                        except Exception as e:
                            last_error = str(e)
                            logger.warning(f"Метод #{i+1} не сработал: {last_error}")
                    
                    if data is None:
                        self.send_json_response(400, {
                            "status": "error", 
                            "message": f"Не удалось прочитать CSV файл: {last_error}. Проверьте формат и кодировку файла."
                        })
                        os.remove(temp_file_path)
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
    