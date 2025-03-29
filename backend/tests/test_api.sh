#!/bin/bash

# Базовый URL API
BASE_URL="http://localhost:8000"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Функция для вывода результатов
print_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
    fi
}

echo "Тестирование API RFM Analyzer"
echo "============================="

# 1. Регистрация нового пользователя
echo -e "\n1. Регистрация пользователя"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "test123",
        "name": "Test User",
        "plan_type": "free"
    }')
echo $REGISTER_RESPONSE | jq '.'
print_result "Регистрация пользователя"

# 2. Получение токена доступа
echo -e "\n2. Получение токена доступа"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=test123")
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.data.access_token')
echo $TOKEN_RESPONSE | jq '.'
print_result "Получение токена"

# 3. Получение информации о пользователе
echo -e "\n3. Информация о пользователе"
USER_INFO=$(curl -s -X GET "$BASE_URL/users/me" \
    -H "Authorization: Bearer $TOKEN")
echo $USER_INFO | jq '.'
print_result "Получение информации о пользователе"

# 4. Загрузка и анализ файла
echo -e "\n4. Загрузка и анализ файла"
# Создаем тестовый CSV файл
echo "customer_id,transaction_date,amount
1,2024-01-01,100
1,2024-01-15,150
2,2024-01-10,200
2,2024-02-01,250
3,2024-02-15,300" > test_data.csv

UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload-and-analyze" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test_data.csv" \
    -F 'params={"recency_column": "transaction_date", "frequency_column": "amount", "monetary_column": "amount", "segments_count": 3}')
echo $UPLOAD_RESPONSE | jq '.'
print_result "Загрузка и анализ файла"

# Получаем ID анализа
ANALYSIS_ID=$(echo $UPLOAD_RESPONSE | jq -r '.data.analysis_result.id')

# 5. Получение истории анализов
echo -e "\n5. История анализов"
HISTORY_RESPONSE=$(curl -s -X GET "$BASE_URL/analysis-history" \
    -H "Authorization: Bearer $TOKEN")
echo $HISTORY_RESPONSE | jq '.'
print_result "Получение истории анализов"

# 6. Получение деталей анализа
echo -e "\n6. Детали анализа"
DETAILS_RESPONSE=$(curl -s -X GET "$BASE_URL/analysis/$ANALYSIS_ID" \
    -H "Authorization: Bearer $TOKEN")
echo $DETAILS_RESPONSE | jq '.'
print_result "Получение деталей анализа"

# 7. Экспорт результатов
echo -e "\n7. Экспорт результатов"
# Экспорт в CSV
curl -s -X GET "$BASE_URL/export/$ANALYSIS_ID?format=csv" \
    -H "Authorization: Bearer $TOKEN" \
    -o "analysis_export.csv"
print_result "Экспорт в CSV"

# Экспорт в Excel
curl -s -X GET "$BASE_URL/export/$ANALYSIS_ID?format=xlsx" \
    -H "Authorization: Bearer $TOKEN" \
    -o "analysis_export.xlsx"
print_result "Экспорт в Excel"

# 8. Обновление тарифного плана
echo -e "\n8. Обновление тарифного плана"
UPDATE_PLAN_RESPONSE=$(curl -s -X POST "$BASE_URL/update-plan?plan_type=basic" \
    -H "Authorization: Bearer $TOKEN")
echo $UPDATE_PLAN_RESPONSE | jq '.'
print_result "Обновление тарифного плана"

# 9. Тестирование ограничений
echo -e "\n9. Тестирование ограничений"
# Попытка загрузить файл размером больше лимита
dd if=/dev/zero of=large_file.csv bs=6M count=1
LARGE_FILE_RESPONSE=$(curl -s -X POST "$BASE_URL/upload-and-analyze" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@large_file.csv" \
    -F 'params={"recency_column": "transaction_date", "frequency_column": "amount", "monetary_column": "amount", "segments_count": 3}')
echo $LARGE_FILE_RESPONSE | jq '.'
print_result "Проверка ограничения размера файла"

# Очистка
rm test_data.csv large_file.csv analysis_export.csv analysis_export.xlsx

echo -e "\nТестирование завершено" 