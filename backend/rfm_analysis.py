import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

def safe_qcut(series: pd.Series, q: int, labels: List[int], default: int = 1) -> pd.Series:
    """
    Безопасное применение pd.qcut с обработкой ошибок на уровне отдельных клиентов.
    
    Args:
        series: Серия данных для квантилизации
        q: Количество квантилей
        labels: Метки для квантилей
        default: Значение по умолчанию при ошибке
    
    Returns:
        pd.Series: Результат квантилизации
    """
    try:
        return pd.qcut(series, q=q, labels=labels)
    except ValueError:
        # Если не удалось разделить на квантили, используем простую сегментацию
        if len(series) == 0:
            return pd.Series(default, index=series.index)
        
        # Разделяем на 4 равные части по значению
        thresholds = series.quantile([0.25, 0.5, 0.75])
        return pd.cut(series, 
                     bins=[-np.inf] + thresholds.tolist() + [np.inf],
                     labels=labels)

def calculate_segment_stats(rfm: pd.DataFrame, customer_column: str) -> Dict[str, Any]:
    """
    Расчет статистики по сегментам.
    
    Args:
        rfm: DataFrame с RFM-метриками
        customer_column: Название колонки с ID клиента
    
    Returns:
        Dict с статистикой по сегментам
    """
    return rfm.groupby('segment').agg({
        customer_column: 'count',
        'monetary': ['mean', 'sum'],
        'frequency': 'mean'
    }).round(2)

def calculate_metrics(rfm: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Расчет метрик RFM.
    
    Args:
        rfm: DataFrame с RFM-метриками
    
    Returns:
        Dict с метриками
    """
    return {
        'recency': {
            'mean': float(rfm['recency'].mean()),
            'median': float(rfm['recency'].median()),
            'std': float(rfm['recency'].std())
        },
        'frequency': {
            'mean': float(rfm['frequency'].mean()),
            'median': float(rfm['frequency'].median()),
            'std': float(rfm['frequency'].std())
        },
        'monetary': {
            'mean': float(rfm['monetary'].mean()),
            'median': float(rfm['monetary'].median()),
            'std': float(rfm['monetary'].std())
        }
    }

def perform_rfm_analysis(
    df: pd.DataFrame,
    date_column: str = 'order_date',
    amount_column: str = 'order_amount',
    customer_column: str = 'customer_id'
) -> Dict[str, Any]:
    """
    Выполняет RFM-анализ на основе транзакционных данных.
    
    Args:
        df (pd.DataFrame): DataFrame с транзакционными данными
        date_column (str): Название колонки с датой транзакции
        amount_column (str): Название колонки с суммой транзакции
        customer_column (str): Название колонки с идентификатором клиента
    
    Returns:
        dict: Результаты RFM-анализа, включая метрики и сегментацию
        
    Raises:
        ValueError: Если отсутствуют необходимые колонки или данные некорректны
    """
    # Валидация входных данных
    required_columns = {date_column, amount_column, customer_column}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Отсутствуют колонки: {required_columns - set(df.columns)}")
    
    # Проверка на пустые значения
    if df[required_columns].isnull().any().any():
        raise ValueError("В данных присутствуют пустые значения")
    
    # Проверка типов данных
    if not pd.api.types.is_numeric_dtype(df[amount_column]):
        raise ValueError(f"Колонка {amount_column} должна содержать числовые значения")
    
    # Конвертация даты
    try:
        df[date_column] = pd.to_datetime(df[date_column])
    except Exception as e:
        raise ValueError(f"Ошибка конвертации даты: {str(e)}")
    
    # Расчет метрик
    current_date = df[date_column].max()
    
    # Оптимизированная группировка с одним проходом
    rfm = df.groupby(customer_column).agg({
        date_column: lambda x: (current_date - x.max()).days,
        amount_column: ['count', 'sum']
    }).reset_index()
    
    rfm.columns = [customer_column, 'recency', 'frequency', 'monetary']
    
    # Нормализация метрик
    rfm['recency'] = rfm['recency'].astype(float)
    rfm['frequency'] = rfm['frequency'].astype(float)
    rfm['monetary'] = rfm['monetary'].astype(float)
    
    # Расчет RFM-баллов (4 квантиля)
    rfm['r_score'] = safe_qcut(rfm['recency'], 4, [4, 3, 2, 1])
    rfm['f_score'] = safe_qcut(rfm['frequency'].rank(method='first'), 4, [1, 2, 3, 4])
    rfm['m_score'] = safe_qcut(rfm['monetary'], 4, [1, 2, 3, 4])
    
    # Расчет общего RFM-балла
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # Сегментация клиентов
    def segment_customers(row):
        rfm_score = int(row['rfm_score'])
        if rfm_score >= 444:
            return 'champions'
        elif rfm_score >= 333:
            return 'loyal'
        elif rfm_score >= 222:
            return 'at_risk'
        else:
            return 'lost'
    
    rfm['segment'] = rfm.apply(segment_customers, axis=1)
    
    # Расчет статистики
    segment_stats = calculate_segment_stats(rfm, customer_column)
    metrics = calculate_metrics(rfm)
    
    # Форматирование результатов
    result = {
        'summary': {
            'total_customers': len(rfm),
            'total_revenue': rfm['monetary'].sum(),
            'avg_order_value': rfm['monetary'].mean(),
            'avg_frequency': rfm['frequency'].mean(),
            'avg_recency': rfm['recency'].mean()
        },
        'segments': {
            segment: {
                'count': int(segment_stats.loc[segment, (customer_column, 'count')]),
                'avg_revenue': float(segment_stats.loc[segment, ('monetary', 'mean')]),
                'total_revenue': float(segment_stats.loc[segment, ('monetary', 'sum')]),
                'avg_frequency': float(segment_stats.loc[segment, ('frequency', 'mean')])
            }
            for segment in segment_stats.index
        },
        'metrics': metrics
    }
    
    return result

def calculate_rfm(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Обертка для обратной совместимости.
    Использует стандартные имена колонок.
    
    Args:
        df (pd.DataFrame): DataFrame с транзакционными данными
    
    Returns:
        dict: Результаты RFM-анализа
    """
    return perform_rfm_analysis(
        df,
        date_column='order_date',
        amount_column='order_amount',
        customer_column='customer_id'
    ) 