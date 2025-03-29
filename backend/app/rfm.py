"""
Модуль для выполнения RFM-анализа и генерации рекомендаций.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pandas import DataFrame
from numpy import ndarray
from openai import OpenAI

from .config import settings
from .models import (
    RFMParams,
    AnalysisResult,
    SegmentInfo,
    SegmentSummary,
    AIRecommendations,
    SegmentRecommendation
)


def calculate_rfm_scores(
    df: DataFrame,
    params: RFMParams,
    analysis_date: Optional[datetime] = None
) -> Tuple[DataFrame, Dict[str, float]]:
    """
    Рассчитывает RFM-метрики для датафрейма.
    
    Args:
        df: Исходный датафрейм с данными
        params: Параметры анализа
        analysis_date: Дата анализа (опционально)
        
    Returns:
        Tuple[DataFrame, Dict[str, float]]: Датафрейм с RFM-метриками и статистику
    """
    if analysis_date is None:
        analysis_date = datetime.now()
    
    # Рассчитываем Recency
    df['recency'] = (analysis_date - pd.to_datetime(df[params.recency_column])).dt.days
    recency_stats = {
        'min_recency': df['recency'].min(),
        'max_recency': df['recency'].max(),
        'mean_recency': df['recency'].mean()
    }
    
    # Рассчитываем Frequency
    frequency_df = df.groupby('customer_id')[params.frequency_column].agg(['count', 'sum'])
    df = df.merge(frequency_df, on='customer_id', suffixes=('', '_freq'))
    frequency_stats = {
        'min_frequency': frequency_df['count'].min(),
        'max_frequency': frequency_df['count'].max(),
        'mean_frequency': frequency_df['count'].mean()
    }
    
    # Рассчитываем Monetary
    monetary_df = df.groupby('customer_id')[params.monetary_column].sum()
    df = df.merge(monetary_df, on='customer_id', suffixes=('', '_mon'))
    monetary_stats = {
        'min_monetary': monetary_df.min(),
        'max_monetary': monetary_df.max(),
        'mean_monetary': monetary_df.mean()
    }
    
    # Нормализуем метрики
    df['r_score'] = (df['recency'] - recency_stats['min_recency']) / (recency_stats['max_recency'] - recency_stats['min_recency'])
    df['f_score'] = (df['count'] - frequency_stats['min_frequency']) / (frequency_stats['max_frequency'] - frequency_stats['min_frequency'])
    df['m_score'] = (df[params.monetary_column] - monetary_stats['min_monetary']) / (monetary_stats['max_monetary'] - monetary_stats['min_monetary'])
    
    # Рассчитываем общий RFM-скор
    df['rfm_score'] = (
        params.recency_weight * (1 - df['r_score']) +  # Инвертируем Recency, так как меньше = лучше
        params.frequency_weight * df['f_score'] +
        params.monetary_weight * df['m_score']
    )
    
    return df, {**recency_stats, **frequency_stats, **monetary_stats}


def segment_customers(df: DataFrame, params: RFMParams) -> List[SegmentInfo]:
    """
    Сегментирует клиентов на основе RFM-метрик.
    
    Args:
        df: Датафрейм с RFM-метриками
        params: Параметры анализа
        
    Returns:
        List[SegmentInfo]: Список сегментов
    """
    # Определяем границы сегментов
    rfm_scores = df['rfm_score'].values
    segment_boundaries = np.linspace(0, 1, params.segments_count + 1)
    
    segments = []
    for i in range(params.segments_count):
        mask = (rfm_scores >= segment_boundaries[i]) & (rfm_scores < segment_boundaries[i + 1])
        segment_df = df[mask]
        
        segment = SegmentInfo(
            segment_id=i,
            name=f"Сегмент {i + 1}",
            description=f"RFM-скор: {segment_boundaries[i]:.2f} - {segment_boundaries[i + 1]:.2f}",
            customer_count=len(segment_df),
            recency_score=segment_df['r_score'].mean(),
            frequency_score=segment_df['f_score'].mean(),
            monetary_score=segment_df['m_score'].mean(),
            rfm_score=segment_df['rfm_score'].mean(),
            percentage=len(segment_df) / len(df) * 100
        )
        segments.append(segment)
    
    return segments


def perform_rfm_analysis(
    df: DataFrame,
    params: RFMParams,
    analysis_date: Optional[datetime] = None
) -> AnalysisResult:
    """
    Выполняет RFM-анализ данных.
    
    Args:
        df: Исходный датафрейм с данными
        params: Параметры анализа
        analysis_date: Дата анализа (опционально)
        
    Returns:
        AnalysisResult: Результат анализа
        
    Raises:
        ValueError: Если данные некорректны или отсутствуют необходимые колонки
    """
    # Проверяем наличие необходимых колонок
    required_columns = [params.recency_column, params.frequency_column, params.monetary_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Отсутствуют необходимые колонки: {', '.join(missing_columns)}")
    
    # Рассчитываем RFM-метрики
    df_with_scores, stats = calculate_rfm_scores(df, params, analysis_date)
    
    # Сегментируем клиентов
    segments = segment_customers(df_with_scores, params)
    
    # Определяем лучший и худший сегменты
    best_segment = max(segments, key=lambda x: x.rfm_score)
    worst_segment = min(segments, key=lambda x: x.rfm_score)
    
    # Создаем сводку
    summary = SegmentSummary(
        total_customers=len(df),
        segments=segments,
        average_rfm_score=df_with_scores['rfm_score'].mean(),
        best_segment=best_segment.name,
        worst_segment=worst_segment.name
    )
    
    return AnalysisResult(
        id="",  # ID будет установлен при сохранении в БД
        user_id="",  # ID пользователя будет установлен при сохранении
        file_id="",  # ID файла будет установлен при сохранении
        params=params,
        summary=summary,
        created_at=datetime.now(),
        status="completed"
    )


def generate_ai_recommendations(
    analysis_result: AnalysisResult,
    business_type: str,
    detail_level: str = "basic"
) -> AIRecommendations:
    """
    Генерирует рекомендации на основе результатов RFM-анализа.
    
    Args:
        analysis_result: Результат RFM-анализа
        business_type: Тип бизнеса (retail, service, etc.)
        detail_level: Уровень детализации (basic/advanced)
        
    Returns:
        AIRecommendations: Рекомендации по сегментам
        
    Raises:
        ValueError: Если не указан API ключ OpenAI
    """
    if not settings.openai_api_key:
        raise ValueError("Не указан API ключ OpenAI")
    
    client = OpenAI(api_key=settings.openai_api_key)
    
    # Формируем промпт для GPT
    prompt = f"""
    На основе результатов RFM-анализа для {business_type} бизнеса, 
    с {len(analysis_result.summary.segments)} сегментами клиентов, 
    сгенерируй рекомендации по работе с каждым сегментом.
    
    Общая статистика:
    - Всего клиентов: {analysis_result.summary.total_customers}
    - Средний RFM-скор: {analysis_result.summary.average_rfm_score:.2f}
    - Лучший сегмент: {analysis_result.summary.best_segment}
    - Худший сегмент: {analysis_result.summary.worst_segment}
    
    Детали по сегментам:
    {[f"Сегмент {s.segment_id + 1}: {s.customer_count} клиентов, RFM-скор: {s.rfm_score:.2f}" for s in analysis_result.summary.segments]}
    
    Пожалуйста, предоставь:
    1. Текущее состояние каждого сегмента
    2. Конкретные действия для улучшения
    3. Ожидаемые результаты
    4. Общую стратегию
    5. Ключевые инсайты
    """
    
    # Получаем ответ от GPT
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты - эксперт по RFM-анализу и маркетинговой стратегии."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    # Парсим ответ и создаем рекомендации
    recommendations = []
    for segment in analysis_result.summary.segments:
        rec = SegmentRecommendation(
            segment_id=segment.segment_id,
            current_state=f"Сегмент с RFM-скором {segment.rfm_score:.2f}",
            actions=["Действие 1", "Действие 2"],  # Заполняется на основе ответа GPT
            expected_outcomes=["Результат 1", "Результат 2"],  # Заполняется на основе ответа GPT
            priority=5 - segment.segment_id  # Приоритет обратно пропорционален номеру сегмента
        )
        recommendations.append(rec)
    
    return AIRecommendations(
        recommendations=recommendations,
        overall_strategy="Общая стратегия",  # Заполняется на основе ответа GPT
        key_insights=["Инсайт 1", "Инсайт 2"],  # Заполняется на основе ответа GPT
        next_steps=["Шаг 1", "Шаг 2"]  # Заполняется на основе ответа GPT
    )
