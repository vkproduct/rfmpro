from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import pandas as pd
from rfm_analysis import perform_rfm_analysis
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder='../frontend')
SECRET_KEY = os.getenv("SECRET_KEY", "my-secret-key-1234567890123456")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def require_auth(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        plan = request.form.get('plan', 'free')
        hashed = pwd_context.hash(password)
        user = supabase.table('users').insert({'email': email, 'password_hash': hashed, 'plan': plan}).execute()
        token = jwt.encode({"sub": user.data[0]['id'], "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = supabase.table('users').select('*').eq('email', email).execute()
        if not user.data or not pwd_context.verify(password, user.data[0]['password_hash']):
            return jsonify({"error": "Неверный email или пароль"}), 401
        token = jwt.encode({"sub": user.data[0]['id'], "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    file = request.files['file']
    data = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
    file.seek(0)
    file_name = f"{request.user_id}_{file.filename}"
    supabase.storage().from_('uploads').upload(file_name, file)
    rfm_result = perform_rfm_analysis(data)
    supabase.table('rfm_results').insert({'user_id': request.user_id, 'file_name': file_name, 'result': rfm_result}).execute()
    return jsonify({"message": "Файл обработан", "rfm": rfm_result})

@app.route('/dashboard')
@require_auth
def dashboard():
    results = supabase.table('rfm_results').select('*').eq('user_id', request.user_id).execute()
    return render_template('dashboard.html', results=results.data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)