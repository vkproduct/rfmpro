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

class UserInfo(UserBase):
    """Модель информации о пользователе."""
    id: str
    name: str
    plan_type: str
    plan_start_date: datetime
    plan_end_date: Optional[datetime] = None
    created_at: datetime

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

class AnalysisParams(BaseModel):
    """Модель параметров анализа."""
    recency_weight: float = Field(ge=0, le=1, default=0.4)
    frequency_weight: float = Field(ge=0, le=1, default=0.3)
    monetary_weight: float = Field(ge=0, le=1, default=0.3)
    segments_count: int = Field(ge=2, le=10, default=3)

class AnalysisSummary(BaseModel):
    """Модель сводки анализа."""
    total_customers: int
    segments: List[SegmentInfo]
    average_rfm_score: float
    best_segment: str
    worst_segment: str

class AnalysisResult(BaseModel):
    """Модель результата анализа."""
    id: str
    user_id: str
    file_id: str
    status: str
    parameters: AnalysisParams
    summary: AnalysisSummary
    recommendations: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Модель ответа с токеном."""
    access_token: str
    token_type: str = "bearer"

class Recommendation(BaseModel):
    """Модель рекомендации."""
    segment: str
    actions: List[str]
    expected_outcomes: List[str]
    priority: str

class Recommendations(BaseModel):
    """Модель рекомендаций."""
    general_recommendations: List[str]
    segment_recommendations: List[Recommendation]
    overall_strategy: str
    key_insights: List[str]
