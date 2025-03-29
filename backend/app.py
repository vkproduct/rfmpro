from flask import Flask, request, jsonify, render_template, session
from supabase import create_client, Client
import pandas as pd
from rfm_analysis import perform_rfm_analysis
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from functools import wraps
import os

app = Flask(__name__, template_folder='../frontend')

# Конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Подключение к Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL"),
    os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
)

def require_auth(f):
    """Декоратор для проверки JWT-токена"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Токен не предоставлен"}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload["sub"]
        except JWTError:
            return jsonify({"error": "Недействительный токен"}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            # Проверка пользователя в Supabase
            user = supabase.table('users').select('*').eq('email', email).execute()
            
            if not user.data:
                return jsonify({"error": "Пользователь не найден"}), 401
            
            stored_hash = user.data[0]['password_hash']
            if not pwd_context.verify(password, stored_hash):
                return jsonify({"error": "Неверный пароль"}), 401
            
            # Создание JWT-токена
            token = jwt.encode(
                {
                    "sub": user.data[0]['id'],
                    "exp": datetime.utcnow() + timedelta(hours=1)
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            
            return jsonify({"token": token})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    try:
        # Проверка наличия файла
        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({"error": "Файл не загружен"}), 400
        
        file = request.files['file']
        
        # Проверка формата файла
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({"error": "Поддерживаются только CSV и Excel"}), 400
        
        # Получение имен колонок
        date_column = request.form.get('date_column', 'order_date')
        amount_column = request.form.get('amount_column', 'order_amount')
        customer_column = request.form.get('customer_column', 'customer_id')
        
        # Чтение файла
        try:
            data = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
        except Exception as e:
            return jsonify({"error": f"Ошибка чтения файла: {str(e)}"}), 400
        
        # Проверка наличия необходимых колонок
        required_columns = [date_column, amount_column, customer_column]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return jsonify({"error": f"Отсутствуют колонки: {', '.join(missing_columns)}"}), 400
        
        # Проверка тарифа
        try:
            user = supabase.table('users').select('plan').eq('id', request.user_id).execute()
            plan = user.data[0]['plan']
            if plan == 'free' and len(data) > 100:
                return jsonify({"error": "Превышен лимит бесплатного тарифа (100 записей)"}), 400
        except Exception as e:
            return jsonify({"error": f"Ошибка проверки тарифа: {str(e)}"}), 500
        
        # Сохранение файла
        try:
            file_name = f"{request.user_id}_{file.filename}"
            supabase.storage().from_('uploads').upload(file_name, file)
        except Exception as e:
            return jsonify({"error": f"Ошибка сохранения файла: {str(e)}"}), 500
        
        # RFM-анализ
        try:
            rfm_result = perform_rfm_analysis(
                data,
                date_column=date_column,
                amount_column=amount_column,
                customer_column=customer_column
            )
        except Exception as e:
            return jsonify({"error": f"Ошибка анализа: {str(e)}"}), 500
        
        # Сохранение результатов
        try:
            supabase.table('rfm_results').insert({
                'user_id': request.user_id,
                'file_name': file_name,
                'result': rfm_result,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            return jsonify({"error": f"Ошибка сохранения результатов: {str(e)}"}), 500
        
        return jsonify({
            "message": "Файл успешно обработан",
            "rfm": rfm_result
        })
        
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500

@app.route('/dashboard')
@require_auth
def dashboard():
    try:
        results = supabase.table('rfm_results').select('*').eq('user_id', request.user_id).execute()
        return render_template('dashboard.html', results=results.data)
    except Exception as e:
        return jsonify({"error": f"Ошибка получения результатов: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True) 