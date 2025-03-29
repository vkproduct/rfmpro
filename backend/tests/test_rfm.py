"""
Тесты для RFM-анализа.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.rfm import (
    calculate_rfm_scores,
    segment_customers,
    generate_recommendations,
    validate_data,
    process_file
)

# Тестовые данные
TEST_DATA = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'last_purchase_date': [
        datetime.now() - timedelta(days=10),
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=60),
        datetime.now() - timedelta(days=90),
        datetime.now() - timedelta(days=120)
    ],
    'purchase_count': [5, 3, 2, 1, 1],
    'total_amount': [1000, 500, 300, 100, 50]
})

def test_validate_data():
    """Тест валидации данных."""
    # Корректные данные
    assert validate_data(TEST_DATA) is True
    
    # Отсутствующие колонки
    invalid_data = TEST_DATA.drop('customer_id', axis=1)
    with pytest.raises(ValueError, match="Отсутствуют обязательные колонки"):
        validate_data(invalid_data)
    
    # Некорректные типы данных
    invalid_data = TEST_DATA.copy()
    invalid_data['purchase_count'] = 'invalid'
    with pytest.raises(ValueError, match="Некорректный тип данных"):
        validate_data(invalid_data)
    
    # Отрицательные значения
    invalid_data = TEST_DATA.copy()
    invalid_data['purchase_count'] = -1
    with pytest.raises(ValueError, match="Отрицательные значения"):
        validate_data(invalid_data)

def test_calculate_rfm_scores():
    """Тест расчета RFM-скоров."""
    # Проверяем корректность расчета
    scores = calculate_rfm_scores(
        TEST_DATA,
        recency_weight=0.4,
        frequency_weight=0.3,
        monetary_weight=0.3
    )
    
    # Проверяем наличие всех необходимых колонок
    assert all(col in scores.columns for col in ['recency_score', 'frequency_score', 'monetary_score', 'rfm_score'])
    
    # Проверяем диапазоны скоров
    assert all(scores['recency_score'].between(0, 1))
    assert all(scores['frequency_score'].between(0, 1))
    assert all(scores['monetary_score'].between(0, 1))
    assert all(scores['rfm_score'].between(0, 1))
    
    # Проверяем корректность весов
    assert abs(scores['rfm_score'].mean() - 0.5) < 0.1

def test_segment_customers():
    """Тест сегментации клиентов."""
    # Рассчитываем скоры
    scores = calculate_rfm_scores(
        TEST_DATA,
        recency_weight=0.4,
        frequency_weight=0.3,
        monetary_weight=0.3
    )
    
    # Сегментируем клиентов
    segments = segment_customers(scores, segments_count=3)
    
    # Проверяем корректность сегментации
    assert len(segments) == 3
    assert all(isinstance(segment, dict) for segment in segments)
    assert all('name' in segment for segment in segments)
    assert all('description' in segment for segment in segments)
    assert all('customer_count' in segment for segment in segments)
    assert all('percentage' in segment for segment in segments)
    
    # Проверяем корректность процентов
    total_percentage = sum(segment['percentage'] for segment in segments)
    assert abs(total_percentage - 100) < 0.1

def test_generate_recommendations():
    """Тест генерации рекомендаций."""
    # Рассчитываем скоры и сегментируем
    scores = calculate_rfm_scores(
        TEST_DATA,
        recency_weight=0.4,
        frequency_weight=0.3,
        monetary_weight=0.3
    )
    segments = segment_customers(scores, segments_count=3)
    
    # Генерируем рекомендации
    recommendations = generate_recommendations(segments)
    
    # Проверяем корректность рекомендаций
    assert isinstance(recommendations, dict)
    assert 'general_recommendations' in recommendations
    assert 'segment_recommendations' in recommendations
    assert len(recommendations['segment_recommendations']) == len(segments)
    
    # Проверяем наличие конкретных рекомендаций
    assert len(recommendations['general_recommendations']) > 0
    assert all(len(rec['recommendations']) > 0 for rec in recommendations['segment_recommendations'])

def test_process_file():
    """Тест обработки файла."""
    # Создаем тестовый файл
    test_file = "test_data.csv"
    TEST_DATA.to_csv(test_file, index=False)
    
    try:
        # Обрабатываем файл
        result = process_file(
            test_file,
            recency_weight=0.4,
            frequency_weight=0.3,
            monetary_weight=0.3,
            segments_count=3
        )
        
        # Проверяем структуру результата
        assert isinstance(result, dict)
        assert 'summary' in result
        assert 'segments' in result
        assert 'recommendations' in result
        
        # Проверяем корректность данных
        assert result['summary']['total_customers'] == len(TEST_DATA)
        assert len(result['segments']) == 3
        assert isinstance(result['recommendations'], dict)
        
    finally:
        # Очищаем тестовый файл
        import os
        if os.path.exists(test_file):
            os.remove(test_file)

def test_edge_cases():
    """Тест граничных случаев."""
    # Пустой датафрейм
    empty_data = pd.DataFrame(columns=TEST_DATA.columns)
    with pytest.raises(ValueError, match="Пустой датафрейм"):
        validate_data(empty_data)
    
    # Один клиент
    single_customer = TEST_DATA.iloc[[0]]
    scores = calculate_rfm_scores(
        single_customer,
        recency_weight=0.4,
        frequency_weight=0.3,
        monetary_weight=0.3
    )
    segments = segment_customers(scores, segments_count=3)
    assert len(segments) == 1
    
    # Максимальные значения
    max_data = TEST_DATA.copy()
    max_data['purchase_count'] = 1000
    max_data['total_amount'] = 1000000
    scores = calculate_rfm_scores(
        max_data,
        recency_weight=0.4,
        frequency_weight=0.3,
        monetary_weight=0.3
    )
    assert all(scores['rfm_score'].between(0, 1))

def test_performance():
    """Тест производительности."""
    # Создаем большой датафрейм
    large_data = pd.DataFrame({
        'customer_id': range(10000),
        'last_purchase_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(10000)],
        'purchase_count': np.random.randint(1, 100, 10000),
        'total_amount': np.random.randint(100, 10000, 10000)
    })
    
    # Проверяем время выполнения
    import time
    start_time = time.time()
    
    scores = calculate_rfm_scores(
        large_data,
        recency_weight=0.4,
        frequency_weight=0.3,
        monetary_weight=0.3
    )
    segments = segment_customers(scores, segments_count=5)
    recommendations = generate_recommendations(segments)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Проверяем, что обработка выполняется достаточно быстро
    assert execution_time < 5  # секунд 