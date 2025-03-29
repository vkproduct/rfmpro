import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.rfm import perform_rfm_analysis, generate_ai_recommendations
from app.models import RFMParams

def test_rfm_analysis():
    """Тестирование RFM-анализа"""
    # Создаем тестовые данные
    dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
    data = {
        'customer_id': np.repeat(range(1, 6), 10),
        'transaction_date': np.random.choice(dates, 50),
        'amount': np.random.randint(100, 1000, 50)
    }
    df = pd.DataFrame(data)
    
    # Параметры анализа
    params = RFMParams(
        recency_column='transaction_date',
        frequency_column='amount',
        monetary_column='amount',
        segments_count=3,
        recency_weight=1.0,
        frequency_weight=1.0,
        monetary_weight=1.0
    )
    
    # Выполняем анализ
    result = perform_rfm_analysis(df, params)
    
    # Проверяем результаты
    assert len(result.summary.segments) == 3, "Неверное количество сегментов"
    assert result.summary.total_customers == 5, "Неверное количество клиентов"
    assert 0 <= result.summary.average_rfm_score <= 1, "RFM-скор вне допустимого диапазона"
    
    # Проверяем сегменты
    for segment in result.summary.segments:
        assert 0 <= segment.rfm_score <= 1, f"RFM-скор сегмента {segment.segment_id} вне диапазона"
        assert 0 <= segment.percentage <= 100, f"Процент сегмента {segment.segment_id} вне диапазона"
        assert segment.customer_count > 0, f"Нулевое количество клиентов в сегменте {segment.segment_id}"
    
    print("✓ RFM-анализ работает корректно")

def test_recommendations():
    """Тестирование генерации рекомендаций"""
    # Создаем тестовые результаты анализа
    segments = [
        {
            "segment_id": 0,
            "name": "Segment 1",
            "description": "Best customers",
            "customer_count": 100,
            "recency_score": 0.9,
            "frequency_score": 0.8,
            "monetary_score": 0.9,
            "rfm_score": 0.87,
            "percentage": 20
        },
        {
            "segment_id": 1,
            "name": "Segment 2",
            "description": "Average customers",
            "customer_count": 300,
            "recency_score": 0.5,
            "frequency_score": 0.6,
            "monetary_score": 0.5,
            "rfm_score": 0.53,
            "percentage": 60
        },
        {
            "segment_id": 2,
            "name": "Segment 3",
            "description": "At-risk customers",
            "customer_count": 100,
            "recency_score": 0.2,
            "frequency_score": 0.3,
            "monetary_score": 0.2,
            "rfm_score": 0.23,
            "percentage": 20
        }
    ]
    
    from app.models import AnalysisResult, SegmentSummary, SegmentInfo
    analysis_result = AnalysisResult(
        id="test_id",
        user_id="test_user",
        file_id="test_file",
        params=RFMParams(
            recency_column="date",
            frequency_column="freq",
            monetary_column="mon",
            segments_count=3
        ),
        summary=SegmentSummary(
            total_customers=500,
            segments=[SegmentInfo(**segment) for segment in segments],
            average_rfm_score=0.54,
            best_segment="Segment 1",
            worst_segment="Segment 3"
        ),
        created_at=datetime.now(),
        status="completed"
    )
    
    # Генерируем рекомендации
    recommendations = generate_ai_recommendations(
        analysis_result,
        business_type="retail",
        detail_level="advanced"
    )
    
    # Проверяем рекомендации
    assert len(recommendations.recommendations) == 3, "Неверное количество рекомендаций"
    
    for rec in recommendations.recommendations:
        assert len(rec.actions) > 0, f"Нет действий для сегмента {rec.segment_id}"
        assert len(rec.expected_outcomes) > 0, f"Нет ожидаемых результатов для сегмента {rec.segment_id}"
        assert rec.current_state, f"Нет текущего состояния для сегмента {rec.segment_id}"
    
    assert recommendations.overall_strategy, "Отсутствует общая стратегия"
    assert len(recommendations.key_insights) > 0, "Отсутствуют ключевые инсайты"
    
    print("✓ Генерация рекомендаций работает корректно")

def test_edge_cases():
    """Тестирование граничных случаев"""
    # Тест с минимальным количеством данных
    minimal_data = pd.DataFrame({
        'customer_id': [1],
        'transaction_date': ['2024-01-01'],
        'amount': [100]
    })
    
    params = RFMParams(
        recency_column='transaction_date',
        frequency_column='amount',
        monetary_column='amount',
        segments_count=2
    )
    
    try:
        result = perform_rfm_analysis(minimal_data, params)
        print("✓ Анализ работает с минимальным количеством данных")
    except Exception as e:
        print(f"✗ Ошибка при анализе минимальных данных: {str(e)}")
    
    # Тест с большим количеством данных
    large_data = pd.DataFrame({
        'customer_id': np.repeat(range(1, 1001), 10),
        'transaction_date': np.random.choice(pd.date_range('2024-01-01', '2024-03-01'), 10000),
        'amount': np.random.randint(100, 1000, 10000)
    })
    
    try:
        result = perform_rfm_analysis(large_data, params)
        print("✓ Анализ работает с большим количеством данных")
    except Exception as e:
        print(f"✗ Ошибка при анализе большого количества данных: {str(e)}")

if __name__ == "__main__":
    print("Запуск тестов RFM-анализа")
    print("=========================")
    
    test_rfm_analysis()
    test_recommendations()
    test_edge_cases()
    
    print("\nТестирование завершено") 