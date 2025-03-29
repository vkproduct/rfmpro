from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
import pandas as pd
import os
from dotenv import load_dotenv
import chardet
import csv

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
        # Проверка формата файла
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")

        # Чтение файла в зависимости от расширения
        if file.filename.endswith('.csv'):
            try:
                # Читаем содержимое файла один раз
                raw_data = file.file.read()
                
                # Определение кодировки
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                print(f"Определена кодировка: {encoding}")
                
                # Если кодировка не определена, пробуем стандартные варианты
                if not encoding:
                    encodings = ['utf-8', 'cp1251', 'latin1', 'iso-8859-5']
                    for enc in encodings:
                        try:
                            decoded_data = raw_data.decode(enc)
                            encoding = enc
                            print(f"Использована кодировка: {enc}")
                            break
                        except Exception as e:
                            print(f"Ошибка при декодировании {enc}: {str(e)}")
                            continue
                    if not encoding:
                        raise HTTPException(status_code=400, detail="Не удалось определить кодировку файла")
                
                # Декодируем данные
                try:
                    decoded_data = raw_data.decode(encoding)
                    print(f"Данные успешно декодированы, длина: {len(decoded_data)}")
                except Exception as e:
                    print(f"Ошибка декодирования: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Ошибка декодирования файла. Кодировка: {encoding}")
                
                # Определение разделителя
                try:
                    dialect = csv.Sniffer().sniff(decoded_data)
                    separator = dialect.delimiter
                    print(f"Определен разделитель: '{separator}'")
                except Exception as e:
                    print(f"Ошибка определения разделителя: {str(e)}")
                    # Если не удалось определить разделитель, пробуем разные варианты
                    separators = [',', ';', '\t']
                    for sep in separators:
                        try:
                            pd.read_csv(pd.io.StringIO(decoded_data), sep=sep)
                            separator = sep
                            print(f"Использован разделитель: '{sep}'")
                            break
                        except Exception as e:
                            print(f"Ошибка при проверке разделителя '{sep}': {str(e)}")
                            continue
                    else:
                        raise HTTPException(status_code=400, detail="Не удалось определить разделитель в файле")
                
                # Чтение файла с определенными параметрами
                try:
                    df = pd.read_csv(
                        pd.io.StringIO(decoded_data),
                        sep=separator,
                        on_bad_lines='skip',
                        dtype=str,
                        encoding=encoding
                    )
                    print(f"Файл успешно прочитан, колонки: {df.columns.tolist()}")
                    print(f"Количество строк: {len(df)}")
                except Exception as e:
                    print(f"Ошибка при чтении CSV: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Ошибка при чтении CSV: {str(e)}")
                
                # Проверка наличия данных
                if df.empty:
                    raise HTTPException(status_code=400, detail="Файл не содержит данных")
                
                # Конвертация числовых колонок
                try:
                    df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    print(f"Данные успешно конвертированы")
                except Exception as e:
                    print(f"Ошибка при конвертации данных: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Ошибка при конвертации данных: {str(e)}")
            except Exception as e:
                print(f"Общая ошибка при обработке CSV: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Ошибка при обработке CSV файла: {str(e)}")
        else:
            df = pd.read_excel(file.file)

        # Проверка наличия необходимых колонок
        required_cols = [client_id_col, date_col, amount_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Отсутствуют необходимые колонки: {', '.join(missing_cols)}")

        # Подготовка данных
        data = df[[client_id_col, date_col, amount_col]].rename(columns={
            client_id_col: "client_id",
            date_col: "date",
            amount_col: "amount"
        }).to_dict(orient="records")

        # Добавление user_id к каждой записи
        for record in data:
            record["user_id"] = user_id
            # Преобразование типов данных
            record["client_id"] = str(record["client_id"])
            record["date"] = str(record["date"])
            record["amount"] = float(record["amount"])

        # Сохранение в Supabase
        response = supabase.table("purchases").insert(data).execute()
        
        if response.error:
            raise HTTPException(status_code=500, detail="Ошибка сохранения данных")

        return {"message": "Данные успешно загружены", "count": len(data)}
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Файл пуст")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Ошибка при чтении файла. Проверьте формат данных")
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