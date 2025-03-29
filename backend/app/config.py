"""
Модуль конфигурации для RFM-анализатора.
Содержит настройки приложения.
"""

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения.
    """
    # Настройки приложения
    app_name: str = "RFM Analyzer"
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # Настройки безопасности
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    access_token_expire_minutes: int = 60 * 24  # 24 часа
    
    # Настройки Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # Настройки файлов
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10 МБ
    
    # Лимиты планов
    free_plan_limit: int = 100
    basic_plan_limit: int = 1000
    
    # Настройки AI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем экземпляр настроек
settings = Settings()
