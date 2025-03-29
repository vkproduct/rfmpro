"""
Модуль аутентификации для RFM-анализатора.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client

from .config import settings
from .models import User, TokenData, UserCreate, UserLogin

# Инициализация криптографического контекста
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Инициализация OAuth2 схемы
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/token")

# Инициализация Supabase клиента
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля его хешу.
    
    Args:
        plain_password: Исходный пароль
        hashed_password: Хеш пароля
        
    Returns:
        bool: True если пароль соответствует хешу
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля.
    
    Args:
        password: Исходный пароль
        
    Returns:
        str: Хеш пароля
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.
    
    Args:
        data: Данные для токена
        expires_delta: Время жизни токена
        
    Returns:
        str: JWT токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Проверяет JWT токен.
    
    Args:
        token: JWT токен
        
    Returns:
        Optional[TokenData]: Данные токена или None
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            return None
        return TokenData(email=email, user_id=user_id)
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Получает текущего пользователя по токену.
    
    Args:
        token: JWT токен
        
    Returns:
        User: Модель пользователя
        
    Raises:
        HTTPException: Если пользователь не найден или токен недействителен
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
        
    # Получаем пользователя из Supabase
    response = supabase.table("users").select("*").eq("id", token_data.user_id).execute()
    if not response.data:
        raise credentials_exception
        
    user_data = response.data[0]
    return User(**user_data)


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя.
    
    Args:
        email: Email пользователя
        password: Пароль
        
    Returns:
        Optional[User]: Модель пользователя или None
    """
    # Получаем пользователя из Supabase
    response = supabase.table("users").select("*").eq("email", email).execute()
    if not response.data:
        return None
        
    user_data = response.data[0]
    if not verify_password(password, user_data["password_hash"]):
        return None
        
    return User(**user_data)


async def create_user(user: UserCreate) -> User:
    """
    Создает нового пользователя.
    
    Args:
        user: Данные пользователя
        
    Returns:
        User: Созданный пользователь
        
    Raises:
        HTTPException: Если пользователь уже существует
    """
    # Проверяем существование пользователя
    response = supabase.table("users").select("id").eq("email", user.email).execute()
    if response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем пользователя
    user_data = user.dict()
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    user_data["created_at"] = datetime.utcnow()
    
    response = supabase.table("users").insert(user_data).execute()
    return User(**response.data[0])


def check_plan_limits(user: User, data_size: int) -> bool:
    """
    Проверяет соответствие размера данных лимитам плана.
    
    Args:
        user: Пользователь
        data_size: Размер данных
        
    Returns:
        bool: True если данные соответствуют лимитам
    """
    limits = {
        "free": settings.free_plan_limit,
        "basic": settings.basic_plan_limit,
        "pro": float("inf")
    }
    return data_size <= limits.get(user.plan_type, limits["free"])

def is_premium_feature(feature: str) -> bool:
    """Проверка доступности премиум-функций"""
    premium_features = {
        "excel_export": ["basic", "pro"],
        "ai_recommendations": ["pro"],
        "api_access": ["pro"],
        "advanced_analytics": ["pro"]
    }
    
    return feature in premium_features
