import http.server
import socketserver
import pandas as pd
from rfmpro_analysis import rfmpro_analysis
import os
import json
import requests
from datetime import datetime

PORT = 8000
POCKETBASE_URL = "http://127.0.0.1:8090/api"

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("static/index.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open("static/style.css", "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')

            if self.path == '/register':
                data = dict(x.split('=') for x in post_data.decode('utf-8').split('&'))
                email = data.get('email')
                password = data.get('password')
                response = requests.post(
                    f"{POCKETBASE_URL}/collections/users/records",
                    json={"email": email, "password": password, "passwordConfirm": password}
                )
                if response.status_code == 201:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "Регистрация прошла успешно"}).encode())
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": response.text}).encode())

            elif self.path == '/login':
                data = dict(x.split('=') for x in post_data.decode('utf-8').split('&'))
                email = data.get('email')
                password = data.get('password')
                response = requests.post(
                    f"{POCKETBASE_URL}/collections/users/auth-with-password",
                    json={"identity": email, "password": password}
                )
                if response.status_code == 200:
                    auth_token = response.json()['token']
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("X-Auth-Token", auth_token)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "Вход успешен"}).encode())
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Неверные данные"}).encode())

            elif self.path == '/upload':
                auth = self.headers.get('Authorization', '')
                if not auth:
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
                
                rfm_df, additional_info = rfmpro_analysis(data, date_col, customer_col, amount_col)
                rfm_result = {
                    "total_customers": int(rfm_df[customer_col].nunique()),
                    "total_revenue": float(rfm_df['Monetary'].sum()),
                    "segments": additional_info['segment_distribution'].set_index('Customer_Segment')['Count'].to_dict()
                }
                
                with open(file_name, 'rb') as f:
                    files = {'file': (file_name, f, 'text/csv')}
                    upload_response = requests.post(
                        f"{POCKETBASE_URL}/collections/uploads/records",
                        headers={"Authorization": auth},
                        files=files
                    )
                if upload_response.status_code != 201:
                    raise Exception("Ошибка загрузки файла: " + upload_response.text)

                result_response = requests.post(
                    f"{POCKETBASE_URL}/collections/rfm_results/records",
                    headers={"Authorization": auth},
                    json={"file_name": file_name, "result": rfm_result}
                )
                if result_response.status_code != 201:
                    raise Exception("Ошибка сохранения результата: " + result_response.text)

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(rfm_result).encode())

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode()))

    def check_auth(self, auth_header):
        response = requests.get(
            f"{POCKETBASE_URL}/collections/users/auth-refresh",
            headers={"Authorization": auth_header}
        )
        return response.status_code == 200

Handler = SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Сервер запущен на http://localhost:{PORT}")
    httpd.serve_forever()