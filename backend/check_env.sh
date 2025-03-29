#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Функция для проверки версии Python
check_python_version() {
    echo -e "${YELLOW}Проверка версии Python...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Ошибка: Python 3 не установлен${NC}"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo -e "${RED}Ошибка: требуется Python 3.8 или выше${NC}"
        echo -e "${RED}Текущая версия: $PYTHON_VERSION${NC}"
        echo -e "${YELLOW}Пожалуйста, установите Python 3.8+ и попробуйте снова${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Python $PYTHON_VERSION OK${NC}"
    return 0
}

# Функция для проверки pip
check_pip() {
    echo -e "${YELLOW}Проверка pip...${NC}"
    
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}Ошибка: pip3 не найден${NC}"
        echo -e "${YELLOW}Пожалуйста, установите pip для Python 3${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ pip3 OK${NC}"
    return 0
}

# Функция для проверки venv
check_venv_module() {
    echo -e "${YELLOW}Проверка модуля venv...${NC}"
    
    if ! python3 -c "import venv" &> /dev/null; then
        echo -e "${RED}Ошибка: модуль venv не установлен${NC}"
        echo -e "${YELLOW}Пожалуйста, установите модуль venv для Python 3${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ venv модуль OK${NC}"
    return 0
}

# Функция для создания виртуального окружения
create_venv() {
    echo -e "${YELLOW}Проверка виртуального окружения...${NC}"
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Создание виртуального окружения...${NC}"
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}Ошибка при создании виртуального окружения${NC}"
            return 1
        fi
        echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
    else
        echo -e "${GREEN}✓ Виртуальное окружение существует${NC}"
    fi
    return 0
}

# Функция для установки зависимостей
install_dependencies() {
    echo -e "${YELLOW}Установка зависимостей...${NC}"
    
    # Активируем виртуальное окружение
    source venv/bin/activate
    
    # Проверяем активацию
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${RED}Ошибка: не удалось активировать виртуальное окружение${NC}"
        return 1
    fi
    
    # Обновляем pip
    pip install --upgrade pip
    
    # Устанавливаем зависимости
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Ошибка при установке зависимостей${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Зависимости установлены${NC}"
    return 0
}

# Основная функция проверки
main() {
    echo -e "${YELLOW}Начало проверки окружения...${NC}"
    
    # Проверяем Python
    check_python_version || exit 1
    
    # Проверяем pip
    check_pip || exit 1
    
    # Проверяем venv
    check_venv_module || exit 1
    
    # Создаем виртуальное окружение
    create_venv || exit 1
    
    # Устанавливаем зависимости
    install_dependencies || exit 1
    
    echo -e "${GREEN}✓ Все проверки пройдены успешно${NC}"
    echo -e "\n${YELLOW}Инструкции по использованию:${NC}"
    echo -e "1. Активация окружения:"
    echo -e "   source venv/bin/activate  # для Linux/Mac"
    echo -e "   venv\\Scripts\\activate     # для Windows"
    echo -e "\n2. Запуск приложения:"
    echo -e "   cd backend"
    echo -e "   python -m uvicorn app.main:app --reload"
}

# Запускаем проверку
main 