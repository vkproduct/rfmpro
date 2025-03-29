"""
Основной модуль API для RFM-анализатора.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta, datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import io
import os
from supabase import create_client, Client
from .config import settings
from .models import (
    UserCreate, UserInfo, APIResponse, RFMParams, 
    FileInfo, AnalysisResult, AIRecommendation,
    User,
    Token,
    UserLogin
)
from .auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    check_plan_limits,
    authenticate_user,
    create_user
)
from .rfm import perform_rfm_analysis, generate_ai_recommendations
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import tempfile
import shutil

# Инициализация FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API для RFM-анализа клиентской базы",
    version="1.0.0",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация Supabase
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Создаем директорию для загрузок, если её нет
os.makedirs(settings.upload_dir, exist_ok=True)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации запросов."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse(
            success=False,
            message="Ошибка валидации данных",
            error=str(exc)
        ).dict()
    )

@app.exception_handler(ValidationError)
async def pydantic_exception_handler(request: Request, exc: ValidationError):
    """Обработчик ошибок валидации Pydantic."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse(
            success=False,
            message="Ошибка валидации данных",
            error=str(exc)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик общих ошибок."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            message="Внутренняя ошибка сервера",
            error=str(exc)
        ).dict()
    )

@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return APIResponse(
        success=True,
        message="API RFM-анализатора работает",
        data={"version": "1.0.0"}
    )

@app.post("/token", response_model=APIResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Получение токена доступа"""
    try:
        # Получение пользователя из Supabase
        user_data = supabase.table("users").select("*").eq("email", form_data.username).execute()
        
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_data.data[0]
        
        # Проверка пароля
        if not verify_password(form_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создание токена
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user["id"]}, expires_delta=access_token_expires
        )
        
        return APIResponse(
            success=True,
            message="Успешная аутентификация",
            data={"access_token": access_token, "token_type": "bearer"}
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Ошибка аутентификации",
            error=str(e)
        )

@app.post("/register", response_model=APIResponse)
async def register_user(user: UserCreate):
    """Регистрация нового пользователя"""
    try:
        # Проверка существования пользователя
        existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создание нового пользователя
        user_data = {
            "email": user.email,
            "password_hash": get_password_hash(user.password),
            "name": user.name,
            "plan_type": user.plan_type,
            "created_at": "now()"
        }
        
        result = supabase.table("users").insert(user_data).execute()
        
        return APIResponse(
            success=True,
            message="Пользователь успешно зарегистрирован",
            data={"user_id": result.data[0]["id"]}
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Ошибка регистрации",
            error=str(e)
        )

@app.post("/login", response_model=APIResponse)
async def login_user(user: UserCreate):
    """Вход пользователя"""
    try:
        # Получение пользователя
        user_data = supabase.table("users").select("*").eq("email", user.email).execute()
        
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        db_user = user_data.data[0]
        
        # Проверка пароля
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Создание токена
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": db_user["id"]}, expires_delta=access_token_expires
        )
        
        # Обновление времени последнего входа
        supabase.table("users").update({"last_login": "now()"}).eq("id", db_user["id"]).execute()
        
        return APIResponse(
            success=True,
            message="Успешный вход",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": db_user["id"],
                    "email": db_user["email"],
                    "name": db_user["name"],
                    "plan_type": db_user["plan_type"]
                }
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Ошибка входа",
            error=str(e)
        )

@app.get("/users/me", response_model=APIResponse)
async def read_users_me(current_user: UserInfo = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    try:
        return APIResponse(
            success=True,
            message="Информация о пользователе получена",
            data={
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "plan_type": current_user.plan_type,
                "created_at": current_user.created_at,
                "last_login": current_user.last_login,
                "analysis_count": current_user.analysis_count,
                "is_active": current_user.is_active
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Ошибка получения информации о пользователе",
            error=str(e)
        )

@app.post(f"{settings.api_prefix}/upload-and-analyze", response_model=APIResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    recency_column: str = Query(..., description="Колонка с датами"),
    frequency_column: str = Query(..., description="Колонка с частотой"),
    monetary_column: str = Query(..., description="Колонка с суммами"),
    segments_count: int = Query(5, ge=2, le=10, description="Количество сегментов"),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка файла и выполнение RFM-анализа.
    
    Args:
        file: CSV файл с данными
        recency_column: Колонка с датами
        frequency_column: Колонка с частотой
        monetary_column: Колонка с суммами
        segments_count: Количество сегментов
        current_user: Текущий пользователь
        
    Returns:
        APIResponse: Результат анализа
    """
    try:
        # Проверяем размер файла
        file_size = 0
        file_path = os.path.join(settings.upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > settings.max_file_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Файл слишком большой"
                    )
                buffer.write(chunk)
        
        # Проверяем лимиты плана
        if not check_plan_limits(current_user, file_size):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Превышен лимит размера файла для вашего плана"
            )
        
        # Сохраняем информацию о файле
        file_info = FileInfo(
            id=str(datetime.now().timestamp()),
            user_id=current_user.id,
            filename=file.filename,
            file_size=file_size,
            uploaded_at=datetime.now(),
            status="processing"
        )
        
        # Читаем данные
        df = pd.read_csv(file_path)
        
        # Выполняем анализ
        params = RFMParams(
            recency_column=recency_column,
            frequency_column=frequency_column,
            monetary_column=monetary_column,
            segments_count=segments_count
        )
        
        result = perform_rfm_analysis(df, params)
        result.user_id = current_user.id
        result.file_id = file_info.id
        
        # Генерируем рекомендации
        recommendations = generate_ai_recommendations(
            result,
            business_type="retail",
            detail_level="advanced" if current_user.plan_type == "pro" else "basic"
        )
        
        # Сохраняем результаты
        supabase.table("analysis_results").insert(result.dict()).execute()
        supabase.table("files").insert(file_info.dict()).execute()
        
        return APIResponse(
            success=True,
            message="Анализ выполнен успешно",
            data={
                "result": result.dict(),
                "recommendations": recommendations.dict()
            }
        )
        
    except Exception as e:
        # Обновляем статус файла в случае ошибки
        if 'file_info' in locals():
            file_info.status = "error"
            file_info.error_message = str(e)
            supabase.table("files").insert(file_info.dict()).execute()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get(f"{settings.api_prefix}/analysis-history", response_model=APIResponse)
async def get_analysis_history(
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Получение истории анализов пользователя.
    
    Args:
        current_user: Текущий пользователь
        limit: Количество записей
        offset: Смещение
        
    Returns:
        APIResponse: История анализов
    """
    try:
        response = supabase.table("analysis_results")\
            .select("*")\
            .eq("user_id", current_user.id)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return APIResponse(
            success=True,
            message="История анализов получена",
            data={"results": response.data}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get(f"{settings.api_prefix}/analysis/{analysis_id}", response_model=APIResponse)
async def get_analysis_details(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Получение деталей конкретного анализа.
    
    Args:
        analysis_id: ID анализа
        current_user: Текущий пользователь
        
    Returns:
        APIResponse: Детали анализа
    """
    try:
        response = supabase.table("analysis_results")\
            .select("*")\
            .eq("id", analysis_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Анализ не найден"
            )
        
        return APIResponse(
            success=True,
            message="Детали анализа получены",
            data={"result": response.data[0]}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get(f"{settings.api_prefix}/export/{analysis_id}")
async def export_analysis(
    analysis_id: str,
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: User = Depends(get_current_user)
):
    """
    Экспорт результатов анализа.
    
    Args:
        analysis_id: ID анализа
        format: Формат экспорта (csv/excel)
        current_user: Текущий пользователь
        
    Returns:
        StreamingResponse: Файл с результатами
        
    Raises:
        HTTPException: Если анализ не найден или произошла ошибка при экспорте
    """
    try:
        # Получаем результаты анализа
        response = supabase.table("analysis_results")\
            .select("*")\
            .eq("id", analysis_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Анализ не найден"
            )
        
        result = response.data[0]
        
        # Создаем временную директорию для экспорта
        with tempfile.TemporaryDirectory() as temp_dir:
            # Подготавливаем данные для экспорта
            export_data = prepare_export_data(result)
            
            # Создаем DataFrame
            df = pd.DataFrame(export_data)
            
            # Формируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfm_analysis_{analysis_id}_{timestamp}"
            
            if format == "csv":
                # Экспортируем в CSV
                file_path = os.path.join(temp_dir, f"{filename}.csv")
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                return FileResponse(
                    file_path,
                    media_type="text/csv",
                    filename=f"{filename}.csv",
                    background=None  # Важно для корректной очистки временных файлов
                )
            else:
                # Экспортируем в Excel
                file_path = os.path.join(temp_dir, f"{filename}.xlsx")
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Основные результаты
                    df.to_excel(writer, sheet_name='Результаты', index=False)
                    
                    # Детали по сегментам
                    segments_df = pd.DataFrame(result['summary']['segments'])
                    segments_df.to_excel(writer, sheet_name='Сегменты', index=False)
                    
                    # Метрики
                    metrics_df = pd.DataFrame([{
                        'Всего клиентов': result['summary']['total_customers'],
                        'Средний RFM-скор': result['summary']['average_rfm_score'],
                        'Лучший сегмент': result['summary']['best_segment'],
                        'Худший сегмент': result['summary']['worst_segment']
                    }])
                    metrics_df.to_excel(writer, sheet_name='Метрики', index=False)
                
                return FileResponse(
                    file_path,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    filename=f"{filename}.xlsx",
                    background=None  # Важно для корректной очистки временных файлов
                )
    
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для экспорта"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при экспорте: {str(e)}"
        )

def prepare_export_data(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Подготовка данных для экспорта.
    
    Args:
        result: Результаты анализа
        
    Returns:
        List[Dict[str, Any]]: Подготовленные данные
    """
    export_data = []
    
    # Добавляем информацию о каждом сегменте
    for segment in result['summary']['segments']:
        export_data.append({
            'Сегмент': segment['name'],
            'Описание': segment['description'],
            'Количество клиентов': segment['customer_count'],
            'Процент': f"{segment['percentage']:.1f}%",
            'RFM-скор': f"{segment['rfm_score']:.3f}",
            'Recency-скор': f"{segment['recency_score']:.3f}",
            'Frequency-скор': f"{segment['frequency_score']:.3f}",
            'Monetary-скор': f"{segment['monetary_score']:.3f}"
        })
    
    return export_data

@app.post("/update-plan", response_model=APIResponse)
async def update_user_plan(
    plan_type: str = Query(..., regex="^(free|basic|pro)$"),
    current_user: UserInfo = Depends(get_current_user)
):
    """Обновление тарифного плана пользователя"""
    try:
        # Проверка возможности обновления плана
        if current_user.plan_type == "pro" and plan_type != "pro":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невозможно понизить план с pro"
            )
        
        # Обновление плана
        supabase.table("users").update({
            "plan_type": plan_type,
            "updated_at": "now()"
        }).eq("id", current_user.id).execute()
        
        return APIResponse(
            success=True,
            message="Тарифный план успешно обновлен",
            data={"plan_type": plan_type}
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Ошибка обновления тарифного плана",
            error=str(e)
        )

@app.post(f"{settings.api_prefix}/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Аутентификация пользователя и получение токена.
    
    Args:
        form_data: Данные формы (username=email, password)
        
    Returns:
        Token: Токен доступа
        
    Raises:
        HTTPException: Если аутентификация не удалась
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.get(f"{settings.api_prefix}/users/me", response_model=APIResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем пользователе.
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        APIResponse: Информация о пользователе
    """
    return APIResponse(
        success=True,
        message="Информация о пользователе получена",
        data={"user": current_user.dict()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
