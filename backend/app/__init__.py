"""
RFM Analyzer - пакет для анализа клиентской базы с использованием RFM-методологии
"""

from .config import settings
from .models import (
    UserBase, UserCreate, UserLogin, UserInfo,
    FileInfo, RFMParams, SegmentInfo, SegmentSummary,
    AnalysisResult, ActionItem, SegmentRecommendation,
    AIRecommendation, AnalysisHistory, APIResponse
)
from .auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    check_plan_limits,
    is_premium_feature
)
from .rfm import (
    perform_rfm_analysis,
    generate_ai_recommendations
)

__version__ = "1.0.0"
__author__ = "RFM Analyzer Team"
__all__ = [
    # Конфигурация
    'settings',
    
    # Модели
    'UserBase', 'UserCreate', 'UserLogin', 'UserInfo',
    'FileInfo', 'RFMParams', 'SegmentInfo', 'SegmentSummary',
    'AnalysisResult', 'ActionItem', 'SegmentRecommendation',
    'AIRecommendation', 'AnalysisHistory', 'APIResponse',
    
    # Аутентификация
    'verify_password', 'get_password_hash', 'create_access_token',
    'get_current_user', 'check_plan_limits', 'is_premium_feature',
    
    # RFM анализ
    'perform_rfm_analysis', 'generate_ai_recommendations'
]
