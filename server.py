import http.server
import socketserver
import pandas as pd
from supabase import create_client
from rfm_analysis import perform_rfm_analysis
import os
from dotenv import load_dotenv
import base64
import json
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
PORT = 8000

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
            if self.path == '/register':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = dict(x.split('=') for x in post_data.split('&'))
                email = data.get('email')
                password = data.get('password')
                supabase.table('users').insert({'email': email, 'password': password}).execute()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Регистрация прошла успешно"}).encode())

            elif self.path == '/login':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = dict(x.split('=') for x in post_data.split('&'))
                email = data.get('email')
                password = data.get('password')
                user = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
                if user.data and len(user.data) > 0:
                    auth = base64.b64encode(f"{email}:{password}".encode()).decode()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("X-Auth-Token", auth)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "Вход успешен"}).encode())
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Неверные данные"}).encode())

            elif self.path == '/upload':
                auth = self.headers.get('Authorization', '')
                if not auth or not self.check_auth(auth):
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Требуется авторизация"}).encode())
                    return
                
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                with open("temp.csv", "wb") as f:
                    f.write(post_data)
                
                data = pd.read_csv("temp.csv")
                required_columns = {'customer_id', 'order_date', 'order_amount'}
                if not required_columns.issubset(data.columns):
                    missing = required_columns - set(data.columns)
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": f"Отсутствуют колонки: {missing}"}).encode())
                    return
                
                rfm_result = perform_rfm_analysis(data)
                file_name = f"result_{int(datetime.now().timestamp())}.csv"
                supabase.storage().from_('uploads').upload(file_name, open("temp.csv", 'rb'))
                supabase.table('rfm_results').insert({'file_name': file_name, 'result': rfm_result}).execute()
                
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
        if not auth_header.startswith('Basic '):
            return False
        encoded = auth_header.split(' ')[1]
        email, password = base64.b64decode(encoded).decode('utf-8').split(':')
        user = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
        return user.data and len(user.data) > 0

Handler = SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Сервер запущен на http://localhost:{PORT}")
    httpd.serve_forever()