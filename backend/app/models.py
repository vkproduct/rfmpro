"""
Модуль с моделями данных для RFM-анализатора.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, conint, confloat

# User Models
class UserBase(BaseModel):
    """Базовая модель пользователя."""
    email: EmailStr
    name: str
    plan_type: str = Field(default="free", pattern="^(free|basic|pro)$")

class UserCreate(UserBase):
    """Модель для создания пользователя."""
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Модель для входа пользователя."""
    email: EmailStr
    password: str

class User(UserBase):
    """Полная модель пользователя."""
    id: str
    created_at: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# File Models
class FileInfo(BaseModel):
    """Информация о загруженном файле."""
    id: str
    user_id: str
    filename: str
    file_size: int
    uploaded_at: datetime
    status: str = Field(..., pattern="^(pending|processing|completed|error)$")
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# RFM Analysis Models
class RFMParams(BaseModel):
    """Параметры для RFM-анализа."""
    recency_column: str
    frequency_column: str
    monetary_column: str
    segments_count: conint(ge=2, le=10) = 5
    recency_weight: confloat(ge=0.0, le=1.0) = 1.0
    frequency_weight: confloat(ge=0.0, le=1.0) = 1.0
    monetary_weight: confloat(ge=0.0, le=1.0) = 1.0
    analysis_date: Optional[datetime] = None

class SegmentInfo(BaseModel):
    """Информация о сегменте."""
    segment_id: int
    name: str
    description: str
    customer_count: int
    recency_score: float
    frequency_score: float
    monetary_score: float
    rfm_score: float
    percentage: float

class SegmentSummary(BaseModel):
    """Сводка по сегментам."""
    total_customers: int
    segments: List[SegmentInfo]
    average_rfm_score: float
    best_segment: str
    worst_segment: str

class AnalysisResult(BaseModel):
    """Результат RFM-анализа."""
    id: str
    user_id: str
    file_id: str
    params: RFMParams
    summary: SegmentSummary
    created_at: datetime
    status: str = Field(..., pattern="^(processing|completed|error)$")
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# Recommendation Models
class SegmentRecommendation(BaseModel):
    """Рекомендации по сегменту."""
    segment_id: int
    current_state: str
    actions: List[str]
    expected_outcomes: List[str]
    priority: conint(ge=1, le=5)

class AIRecommendations(BaseModel):
    """ИИ-рекомендации по результатам анализа."""
    recommendations: List[SegmentRecommendation]
    overall_strategy: str
    key_insights: List[str]
    next_steps: List[str]

# History Models
class AnalysisHistory(BaseModel):
    """История анализа."""
    id: str
    user_id: str
    file_id: str
    created_at: datetime
    status: str
    result: Optional[AnalysisResult] = None
    recommendations: Optional[AIRecommendations] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Модель токена доступа."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Данные токена."""
    email: Optional[str] = None
    user_id: Optional[str] = None

class APIResponse(BaseModel):
    """Базовый ответ API."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
