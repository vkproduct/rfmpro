#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Функция для проверки статуса выполнения команды
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Проверяем наличие виртуального окружения
if [ ! -d "../venv" ]; then
    echo -e "${RED}Ошибка: виртуальное окружение не найдено${NC}"
    echo -e "${YELLOW}Запустите сначала: ../check_env.sh${NC}"
    exit 1
fi

# Активируем виртуальное окружение
echo -e "${YELLOW}Активация виртуального окружения...${NC}"
source ../venv/bin/activate
check_status "Активация виртуального окружения"

# Проверяем базовые зависимости
echo -e "${YELLOW}Проверка зависимостей...${NC}"
if ! python -c "import fastapi" &> /dev/null; then
    echo -e "${RED}Ошибка: FastAPI не установлен${NC}"
    echo -e "${YELLOW}Запустите: pip install -r ../requirements.txt${NC}"
    exit 1
fi
check_status "Проверка FastAPI"

# Запускаем тесты API
echo -e "${YELLOW}Запуск тестов API...${NC}"
pytest test_api.py -v
check_status "Тесты API"

# Запускаем тесты RFM-анализа
echo -e "${YELLOW}Запуск тестов RFM-анализа...${NC}"
pytest test_rfm.py -v
check_status "Тесты RFM-анализа"

# Проверяем стиль кода
echo -e "${YELLOW}Проверка стиля кода...${NC}"
flake8 ../app
check_status "Проверка flake8"

# Проверяем покрытие кода
echo -e "${YELLOW}Проверка покрытия кода...${NC}"
pytest --cov=../app --cov-report=term-missing
check_status "Проверка покрытия"

# Деактивируем виртуальное окружение
deactivate

echo -e "${GREEN}Все тесты успешно пройдены!${NC}" 