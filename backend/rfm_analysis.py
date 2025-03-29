import pandas as pd
import numpy as np
from datetime import datetime

def perform_rfm_analysis(
    df: pd.DataFrame,
    date_column: str = 'order_date',
    amount_column: str = 'order_amount',
    customer_column: str = 'customer_id'
) -> dict:
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
    now = datetime.now()
    
    # Recency (дни с последней транзакции)
    rfm = df.groupby(customer_column).agg({
        date_column: lambda x: (now - x.max()).days,
        amount_column: ['count', 'sum']
    }).reset_index()
    
    rfm.columns = [customer_column, 'recency', 'frequency', 'monetary']
    
    # Нормализация метрик
    rfm['recency'] = rfm['recency'].astype(float)
    rfm['frequency'] = rfm['frequency'].astype(float)
    rfm['monetary'] = rfm['monetary'].astype(float)
    
    # Расчет RFM-баллов (4 квантиля)
    try:
        rfm['r_score'] = pd.qcut(rfm['recency'], q=4, labels=[4, 3, 2, 1])
    except ValueError:
        rfm['r_score'] = 1  # Минимальный балл при ошибке
    
    try:
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
    except ValueError:
        rfm['f_score'] = 1  # Минимальный балл при ошибке
    
    try:
        rfm['m_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1, 2, 3, 4])
    except ValueError:
        rfm['m_score'] = 1  # Минимальный балл при ошибке
    
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
    
    # Расчет статистики по сегментам
    segment_stats = rfm.groupby('segment').agg({
        customer_column: 'count',
        'monetary': ['mean', 'sum'],
        'frequency': 'mean'
    }).round(2)
    
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
        'metrics': {
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
    }
    
    return result

# Для обратной совместимости
def calculate_rfm(data):
    """
    Устаревшая функция для обратной совместимости.
    Использует perform_rfm_analysis с предустановленными именами колонок.
    """
    return perform_rfm_analysis(
        data,
        date_column='order_date',
        amount_column='order_amount',
        customer_column='customer_id'
    ) 