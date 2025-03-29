#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Настройка окружения для RFM Analyzer"
echo "===================================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 не установлен${NC}"
    exit 1
fi

# Создаем виртуальное окружение
echo -e "\nСоздание виртуального окружения..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при создании виртуального окружения${NC}"
    exit 1
fi

# Активируем виртуальное окружение
echo -e "\nАктивация виртуального окружения..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при активации виртуального окружения${NC}"
    exit 1
fi

# Обновляем pip
echo -e "\nОбновление pip..."
python3 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при обновлении pip${NC}"
    exit 1
fi

# Устанавливаем зависимости
echo -e "\nУстановка зависимостей..."
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при установке зависимостей${NC}"
    exit 1
fi

# Устанавливаем типы для mypy
echo -e "\nУстановка типов для mypy..."
pip install types-python-jose types-passlib pandas-stubs
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при установке типов${NC}"
    exit 1
fi

# Устанавливаем инструменты разработки
echo -e "\nУстановка инструментов разработки..."
pip install flake8 mypy
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при установке инструментов разработки${NC}"
    exit 1
fi

# Создаем .env файл из примера
echo -e "\nСоздание .env файла..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}Создан файл .env. Пожалуйста, настройте переменные окружения${NC}"
fi

echo -e "\n${GREEN}Настройка окружения завершена успешно!${NC}"
echo -e "Для активации окружения используйте: source venv/bin/activate" 