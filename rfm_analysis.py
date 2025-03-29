import pandas as pd
import numpy as np

def perform_rfm_analysis(df):
    df['order_date'] = pd.to_datetime(df['order_date'])
    now = df['order_date'].max()
    
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (now - x.max()).days,
        'order_amount': ['count', 'sum']
    }).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
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
        'total_customers': len(rfm),
        'total_revenue': float(rfm['monetary'].sum()),
        'segments': rfm.groupby('segment').size().to_dict()
    }
    return result