from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import pandas as pd
import os
from dotenv import load_dotenv
from typing import Optional

# Загрузка переменных окружения
load_dotenv()

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация Supabase клиента
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    client_id_col: str = None,
    date_col: str = None,
    amount_col: str = None
):
    try:
        # Чтение файла в зависимости от расширения
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")

        # Проверка наличия необходимых столбцов
        required_cols = [client_id_col, date_col, amount_col]
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail="Отсутствуют необходимые столбцы")

        # Подготовка данных для Supabase
        records = df[[client_id_col, date_col, amount_col]].to_dict('records')
        for record in records:
            record['user_id'] = "user1"  # Временный user_id
            record['client_id'] = str(record[client_id_col])
            record['purchase_date'] = str(record[date_col])
            record['amount'] = float(record[amount_col])
            del record[client_id_col]
            del record[date_col]
            del record[amount_col]

        # Сохранение в Supabase
        result = supabase.table('purchases').insert(records).execute()
        
        return {"message": "Данные успешно загружены", "count": len(records)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
async def analyze_data():
    try:
        # Получение данных из Supabase
        result = supabase.table('purchases').select("*").eq('user_id', 'user1').execute()
        df = pd.DataFrame(result.data)

        if df.empty:
            raise HTTPException(status_code=404, detail="Данные не найдены")

        # RFM анализ
        current_date = pd.Timestamp.now()
        
        # Recency
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        recency = df.groupby('client_id')['purchase_date'].max()
        recency = (current_date - recency).dt.days

        # Frequency
        frequency = df.groupby('client_id').size()

        # Monetary
        monetary = df.groupby('client_id')['amount'].sum()

        # Объединение метрик
        rfm = pd.DataFrame({
            'Recency': recency,
            'Frequency': frequency,
            'Monetary': monetary
        })

        # Нормализация метрик
        rfm['R_score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
        rfm['F_score'] = pd.qcut(rfm['Frequency'], q=5, labels=[1, 2, 3, 4, 5])
        rfm['M_score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5])

        # Расчет RFM score
        rfm['RFM_Score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

        return rfm.to_dict(orient='records')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 