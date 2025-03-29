from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import jwt
from functools import wraps
from rfm_analysis import perform_rfm_analysis

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__, template_folder='../frontend')

# Получаем переменные окружения
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

# Проверяем наличие необходимых переменных окружения
if not all([SUPABASE_URL, SUPABASE_KEY, SECRET_KEY]):
    raise ValueError("Не все необходимые переменные окружения установлены. Проверьте файл .env")

# Инициализация Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Функция для проверки JWT токена
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Токен отсутствует'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = supabase.table('users').select("*").eq('id', data['user_id']).execute()
            if not current_user.data:
                return jsonify({'error': 'Пользователь не найден'}), 401
        except:
            return jsonify({'error': 'Неверный токен'}), 401
            
        return f(current_user.data[0], *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Получаем пользователя из Supabase
        user = supabase.table('users').select("*").eq('email', email).execute()
        
        if user.data and check_password_hash(user.data[0]['password_hash'], password):
            # Создаем JWT токен
            token = jwt.encode({
                'user_id': user.data[0]['id'],
                'exp': datetime.utcnow() + timedelta(days=1)
            }, SECRET_KEY)
            
            return jsonify({
                'data': {
                    'access_token': token,
                    'token_type': 'bearer'
                }
            })
        
        return jsonify({'error': 'Неверный email или пароль'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Проверяем, существует ли пользователь
        existing_user = supabase.table('users').select("*").eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
        
        # Создаем нового пользователя
        hashed_password = generate_password_hash(password)
        user_data = {
            'email': email,
            'password_hash': hashed_password
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            # Создаем JWT токен
            token = jwt.encode({
                'user_id': result.data[0]['id'],
                'exp': datetime.utcnow() + timedelta(days=1)
            }, SECRET_KEY)
            
            return jsonify({
                'data': {
                    'access_token': token,
                    'token_type': 'bearer'
                }
            })
        
        return jsonify({'error': 'Ошибка при создании пользователя'}), 500
    
    return render_template('register.html')

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    # Получаем результаты анализа для пользователя
    results = supabase.table('analysis_results').select("*").eq('user_id', current_user['id']).execute()
    return render_template('dashboard.html', results=results.data)

@app.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            # Читаем файл
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Получаем параметры анализа
            date_column = request.form.get('date_column', 'order_date')
            amount_column = request.form.get('amount_column', 'order_amount')
            customer_column = request.form.get('customer_column', 'customer_id')
            
            # Проверяем наличие необходимых колонок
            required_columns = [date_column, amount_column, customer_column]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({'error': f'Отсутствуют колонки: {", ".join(missing_columns)}'}), 400
            
            # Выполняем RFM анализ
            rfm_result = perform_rfm_analysis(
                df,
                date_column=date_column,
                amount_column=amount_column,
                customer_column=customer_column
            )
            
            # Сохраняем результат в Supabase
            result_data = {
                'user_id': current_user['id'],
                'result': rfm_result,
                'file_name': file.filename,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Сбрасываем позицию файла перед загрузкой
            file.seek(0)
            
            # Загружаем файл в Supabase Storage
            file_path = f"uploads/{current_user['id']}/{file.filename}"
            supabase.storage.from_('files').upload(file_path, file)
            
            # Сохраняем результат анализа
            result = supabase.table('analysis_results').insert(result_data).execute()
            
            if result.data:
                return jsonify({
                    'data': {
                        'rfm': result_data
                    }
                })
            
            return jsonify({'error': 'Ошибка при сохранении результата'}), 500
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Неподдерживаемый формат файла'}), 400

@app.route('/analysis/<int:analysis_id>')
@token_required
def get_analysis(current_user, analysis_id):
    result = supabase.table('analysis_results').select("*").eq('id', analysis_id).eq('user_id', current_user['id']).execute()
    
    if not result.data:
        return jsonify({'error': 'Результат анализа не найден'}), 404
    
    return jsonify({
        'data': {
            'rfm': result.data[0]
        }
    })

if __name__ == '__main__':
    app.run(debug=True) 