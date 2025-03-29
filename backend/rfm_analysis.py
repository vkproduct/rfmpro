import pandas as pd
import numpy as np
from datetime import datetime

def perform_rfm_analysis(df: pd.DataFrame, date_column: str = 'order_date', amount_column: str = 'order_amount', customer_column: str = 'customer_id') -> dict:
    required_columns = {date_column, amount_column, customer_column}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Отсутствуют колонки: {required_columns - set(df.columns)}")
    
    df[date_column] = pd.to_datetime(df[date_column])
    now = df[date_column].max()
    
    rfm = df.groupby(customer_column).agg({
        date_column: lambda x: (now - x.max()).days,
        amount_column: ['count', 'sum']
    }).reset_index()
    rfm.columns = [customer_column, 'recency', 'frequency', 'monetary']
    
    rfm['r_score'] = pd.qcut(rfm['recency'], q=4, labels=[4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1, 2, 3, 4], duplicates='drop')
    
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    def segment_customers(row):
        rfm_score = int(row['rfm_score'])
        if rfm_score >= 444: return 'champions'
        elif rfm_score >= 333: return 'loyal'
        elif rfm_score >= 222: return 'at_risk'
        else: return 'lost'
    
    rfm['segment'] = rfm.apply(segment_customers, axis=1)
    
    result = {
        'summary': {
            'total_customers': len(rfm),
            'total_revenue': float(rfm['monetary'].sum()),
            'avg_order_value': float(rfm['monetary'].mean())
        },
        'segments': rfm.groupby('segment').agg({
            customer_column: 'count',
            'monetary': 'mean'
        }).rename(columns={customer_column: 'count', 'monetary': 'avg_revenue'}).to_dict(orient='index')
    }
    return result