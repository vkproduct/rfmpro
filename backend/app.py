from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import pandas as pd
from rfm_analysis import calculate_rfm

app = Flask(__name__, template_folder='../frontend')

# Подключение к Supabase (замени URL и KEY на свои из Supabase Dashboard)
supabase: Client = create_client("YOUR_SUPABASE_URL", "YOUR_SUPABASE_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Проверка пользователя в Supabase (дополним позже)
        return jsonify({"message": "Успешный вход"})
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    user_id = request.form['user_id']  # Предполагаем, что пользователь авторизован
    data = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
    
    # Ограничение по тарифу
    user = supabase.table('users').select('plan').eq('id', user_id).execute()
    plan = user.data[0]['plan']
    if plan == 'free' and len(data) > 100:
        return jsonify({"error": "Превышен лимит бесплатного тарифа (100 записей)"}), 400
    
    # Сохранение файла в Supabase Storage
    file_name = f"{user_id}_{file.filename}"
    supabase.storage().from_('uploads').upload(file_name, file)
    
    # RFM-анализ
    rfm_result = calculate_rfm(data)
    supabase.table('rfm_results').insert({'user_id': user_id, 'result': rfm_result.to_dict()}).execute()
    
    return jsonify({"message": "Файл обработан", "rfm": rfm_result.to_dict()})

if __name__ == '__main__':
    app.run(debug=True) 