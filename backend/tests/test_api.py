"""
Тесты для API эндпоинтов.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, AnalysisResult
from app.config import settings
import os
import json
from datetime import datetime

client = TestClient(app)

# Тестовые данные
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User",
    "plan_type": "free"
}

@pytest.fixture
def test_user():
    """Создание тестового пользователя."""
    response = client.post(f"{settings.api_prefix}/register", json=TEST_USER)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def test_token(test_user):
    """Получение токена для тестового пользователя."""
    response = client.post(
        f"{settings.api_prefix}/token",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def test_file():
    """Создание тестового CSV файла."""
    test_data = "customer_id,last_purchase_date,purchase_count,total_amount\n"
    test_data += "1,2024-01-01,5,1000\n"
    test_data += "2,2024-02-01,3,500\n"
    test_data += "3,2024-03-01,1,100\n"
    
    with open("test_data.csv", "w") as f:
        f.write(test_data)
    
    yield "test_data.csv"
    
    # Очистка после тестов
    if os.path.exists("test_data.csv"):
        os.remove("test_data.csv")

def test_register():
    """Тест регистрации пользователя."""
    response = client.post(
        f"{settings.api_prefix}/register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "name": "New User",
            "plan_type": "free"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Пользователь успешно зарегистрирован"
    assert "user_id" in data

def test_register_duplicate_email(test_user):
    """Тест регистрации с существующим email."""
    response = client.post(f"{settings.api_prefix}/register", json=TEST_USER)
    assert response.status_code == 400
    assert "Email уже зарегистрирован" in response.json()["detail"]

def test_get_token(test_user):
    """Тест получения токена."""
    response = client.post(
        f"{settings.api_prefix}/token",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_user_info(test_token):
    """Тест получения информации о пользователе."""
    response = client.get(
        f"{settings.api_prefix}/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert data["name"] == TEST_USER["name"]
    assert data["plan_type"] == TEST_USER["plan_type"]

def test_upload_and_analyze(test_token, test_file):
    """Тест загрузки и анализа файла."""
    with open(test_file, "rb") as f:
        response = client.post(
            f"{settings.api_prefix}/upload-and-analyze",
            headers={"Authorization": f"Bearer {test_token}"},
            files={"file": ("test_data.csv", f, "text/csv")},
            data={
                "recency_weight": "0.4",
                "frequency_weight": "0.3",
                "monetary_weight": "0.3",
                "segments_count": "3"
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "status" in data
    assert data["status"] == "processing"

def test_get_analysis_history(test_token):
    """Тест получения истории анализов."""
    response = client.get(
        f"{settings.api_prefix}/analysis-history",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_analysis_details(test_token, test_file):
    """Тест получения деталей анализа."""
    # Сначала создаем анализ
    with open(test_file, "rb") as f:
        upload_response = client.post(
            f"{settings.api_prefix}/upload-and-analyze",
            headers={"Authorization": f"Bearer {test_token}"},
            files={"file": ("test_data.csv", f, "text/csv")},
            data={
                "recency_weight": "0.4",
                "frequency_weight": "0.3",
                "monetary_weight": "0.3",
                "segments_count": "3"
            }
        )
    analysis_id = upload_response.json()["analysis_id"]
    
    # Получаем детали анализа
    response = client.get(
        f"{settings.api_prefix}/analysis/{analysis_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == analysis_id
    assert "summary" in data
    assert "segments" in data
    assert "recommendations" in data

def test_export_analysis(test_token, test_file):
    """Тест экспорта результатов анализа."""
    # Сначала создаем анализ
    with open(test_file, "rb") as f:
        upload_response = client.post(
            f"{settings.api_prefix}/upload-and-analyze",
            headers={"Authorization": f"Bearer {test_token}"},
            files={"file": ("test_data.csv", f, "text/csv")},
            data={
                "recency_weight": "0.4",
                "frequency_weight": "0.3",
                "monetary_weight": "0.3",
                "segments_count": "3"
            }
        )
    analysis_id = upload_response.json()["analysis_id"]
    
    # Экспортируем в CSV
    response = client.get(
        f"{settings.api_prefix}/export/{analysis_id}?format=csv",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    
    # Экспортируем в Excel
    response = client.get(
        f"{settings.api_prefix}/export/{analysis_id}?format=excel",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]

def test_update_plan(test_token):
    """Тест обновления тарифного плана."""
    response = client.post(
        f"{settings.api_prefix}/update-plan",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"plan_type": "basic"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Тарифный план успешно обновлен"
    
    # Проверяем, что план действительно обновился
    user_response = client.get(
        f"{settings.api_prefix}/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert user_response.json()["plan_type"] == "basic"

def test_invalid_token():
    """Тест запроса с невалидным токеном."""
    response = client.get(
        f"{settings.api_prefix}/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_file_size_limit(test_token):
    """Тест ограничения размера файла."""
    # Создаем большой файл
    with open("large_file.csv", "w") as f:
        f.write("customer_id,last_purchase_date,purchase_count,total_amount\n")
        for i in range(1000000):
            f.write(f"{i},2024-01-01,1,100\n")
    
    with open("large_file.csv", "rb") as f:
        response = client.post(
            f"{settings.api_prefix}/upload-and-analyze",
            headers={"Authorization": f"Bearer {test_token}"},
            files={"file": ("large_file.csv", f, "text/csv")},
            data={
                "recency_weight": "0.4",
                "frequency_weight": "0.3",
                "monetary_weight": "0.3",
                "segments_count": "3"
            }
        )
    assert response.status_code == 400
    assert "Размер файла превышает допустимый лимит" in response.json()["detail"]
    
    # Очистка
    if os.path.exists("large_file.csv"):
        os.remove("large_file.csv") 