from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
import pandas as pd
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Настройка безопасности
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        if user.error:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.data.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    client_id_col: str = None,
    date_col: str = None,
    amount_col: str = None,
    user_id: str = Depends(get_current_user)
):
    try:
        # Чтение файла в зависимости от расширения
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

        # Проверка наличия необходимых колонок
        required_cols = [client_id_col, date_col, amount_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing_cols)}")

        # Подготовка данных
        data = df[[client_id_col, date_col, amount_col]].rename(columns={
            client_id_col: "client_id",
            date_col: "date",
            amount_col: "amount"
        }).to_dict(orient="records")

        # Добавление user_id к каждой записи
        for record in data:
            record["user_id"] = user_id

        # Сохранение в Supabase
        response = supabase.table("purchases").insert(data).execute()
        
        if response.error:
            raise HTTPException(status_code=500, detail="Error saving data")

        return {"message": "Данные успешно загружены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
async def analyze_data(user_id: str = Depends(get_current_user)):
    try:
        # Получение данных пользователя
        response = supabase.table("purchases").select("*").eq("user_id", user_id).execute()
        
        if response.error:
            raise HTTPException(status_code=500, detail="Error fetching data")

        data = response.data
        if not data:
            return {
                "message": "Нет данных для анализа",
                "metrics": None,
                "segments": None,
                "trends": None
            }

        # Преобразование данных в DataFrame
        df = pd.DataFrame(data)
        
        # Конвертация даты
        df['date'] = pd.to_datetime(df['date'])
        
        # Расчет RFM метрик
        now = pd.Timestamp.now()
        rfm = df.groupby('client_id').agg({
            'date': lambda x: (now - x.max()).days,
            'amount': ['count', 'sum']
        }).reset_index()
        
        rfm.columns = ['client_id', 'recency', 'frequency', 'monetary']
        
        # Нормализация метрик
        rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1])
        rfm['f_score'] = pd.qcut(rfm['frequency'], q=5, labels=[1, 2, 3, 4, 5])
        rfm['m_score'] = pd.qcut(rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5])
        
        # Расчет RFM score
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        
        # Сегментация
        segments = {
            'Champions': rfm[rfm['rfm_score'].isin(['555', '554', '544', '545', '454', '455', '445'])],
            'Loyal Customers': rfm[rfm['rfm_score'].isin(['543', '444', '435', '355', '354', '345', '344', '335'])],
            'At Risk': rfm[rfm['rfm_score'].isin(['332', '322', '231', '241', '251', '233', '234'])],
            'Lost': rfm[rfm['rfm_score'].isin(['111', '112', '121', '122', '123', '132', '211', '212', '213', '221', '222', '223', '232'])],
            'Other': rfm[~rfm['rfm_score'].isin(['555', '554', '544', '545', '454', '455', '445', '543', '444', '435', '355', '354', '345', '344', '335', '332', '322', '231', '241', '251', '233', '234', '111', '112', '121', '122', '123', '132', '211', '212', '213', '221', '222', '223', '232'])]
        }
        
        # Подготовка результатов
        result = {
            "metrics": {
                "total_customers": len(rfm),
                "avg_recency": rfm['recency'].mean(),
                "avg_frequency": rfm['frequency'].mean(),
                "avg_monetary": rfm['monetary'].mean()
            },
            "segments": {
                name: len(segment) for name, segment in segments.items()
            },
            "trends": {
                "monthly_sales": df.groupby(df['date'].dt.to_period('M'))['amount'].sum().to_dict(),
                "monthly_customers": df.groupby(df['date'].dt.to_period('M'))['client_id'].nunique().to_dict()
            }
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 