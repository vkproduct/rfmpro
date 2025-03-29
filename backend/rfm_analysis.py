import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

def perform_rfm_analysis(
    df: pd.DataFrame,
    date_column: str,
    amount_column: str,
    customer_column: str
) -> Dict[str, Any]:
    """
    Выполняет RFM-анализ на основе предоставленных данных.
    
    Args:
        df: DataFrame с данными транзакций
        date_column: Название колонки с датами
        amount_column: Название колонки с суммами
        customer_column: Название колонки с ID клиентов
    
    Returns:
        Dict с результатами анализа
    """
    # Конвертируем даты
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Получаем текущую дату
    current_date = df[date_column].max()
    
    # Рассчитываем RFM метрики
    rfm = df.groupby(customer_column).agg({
        date_column: lambda x: (current_date - x.max()).days,  # Recency
        customer_column: 'count',  # Frequency
        amount_column: 'sum'  # Monetary
    }).rename(columns={
        date_column: 'recency',
        customer_column: 'frequency',
        amount_column: 'monetary'
    })
    
    # Нормализация метрик
    rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'], q=5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5])
    
    # Рассчитываем RFM score
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # Сегментация клиентов
    def segment_customers(row):
        rfm_score = int(row['rfm_score'])
        if rfm_score >= 555:
            return 'champions'
        elif rfm_score >= 444:
            return 'loyal'
        elif rfm_score >= 333:
            return 'at_risk'
        else:
            return 'lost'
    
    rfm['segment'] = rfm.apply(segment_customers, axis=1)
    
    # Подсчет статистики по сегментам
    segment_stats = rfm['segment'].value_counts()
    total_customers = len(rfm)
    
    # Формируем результат
    result = {
        "summary": {
            "total_customers": total_customers,
            "segments": {
                segment: {
                    "count": int(count),
                    "percentage": round(count / total_customers * 100, 2)
                }
                for segment, count in segment_stats.items()
            }
        },
        "metrics": {
            "recency": {
                "mean": float(rfm['recency'].mean()),
                "median": float(rfm['recency'].median())
            },
            "frequency": {
                "mean": float(rfm['frequency'].mean()),
                "median": float(rfm['frequency'].median())
            },
            "monetary": {
                "mean": float(rfm['monetary'].mean()),
                "median": float(rfm['monetary'].median())
            }
        }
    }
    
    return result 

def calculate_rfm(data):
    # Предполагаем, что в CSV есть колонки: customer_id, order_date, order_amount
    data['order_date'] = pd.to_datetime(data['order_date'])
    latest_date = data['order_date'].max()
    
    rfm = data.groupby('customer_id').agg({
        'order_date': lambda x: (latest_date - x.max()).days,  # Recency
        'customer_id': 'count',                                # Frequency
        'order_amount': 'sum'                                  # Monetary
    }).rename(columns={
        'order_date': 'recency',
        'customer_id': 'frequency',
        'order_amount': 'monetary'
    })
    
    # Квантили для сегментации
    rfm['r_score'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['m_score'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4])
    
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    return rfm 