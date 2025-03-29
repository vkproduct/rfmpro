#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Проверка окружения для RFM Analyzer"
echo "==================================="

# Проверка версии Python
echo -e "\nПроверка версии Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Python 3 не установлен${NC}"
    exit 1
fi

# Проверка наличия venv
echo -e "\nПроверка модуля venv..."
python3 -c "import venv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Модуль venv не установлен${NC}"
    exit 1
fi

# Создание виртуального окружения
echo -e "\nСоздание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Ошибка при создании виртуального окружения${NC}"
        exit 1
    fi
    echo -e "${GREEN}Виртуальное окружение создано${NC}"
else
    echo -e "${GREEN}Виртуальное окружение уже существует${NC}"
fi

# Активация виртуального окружения
echo -e "\nАктивация виртуального окружения..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при активации виртуального окружения${NC}"
    exit 1
fi

# Проверка pip
echo -e "\nПроверка pip..."
pip --version
if [ $? -ne 0 ]; then
    echo -e "${RED}pip не установлен${NC}"
    exit 1
fi

echo -e "\n${GREEN}Окружение успешно настроено!${NC}"
echo -e "Для активации окружения используйте: source venv/bin/activate" 