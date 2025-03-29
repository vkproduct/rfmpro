# RFM Pro

Веб-сервис для RFM-анализа клиентской базы с использованием FastAPI, Supabase и Web Components.

## Функциональность

- Загрузка CSV/Excel файлов с данными о покупках
- Выбор столбцов для RFM-анализа
- Автоматический расчет RFM-метрик
- Визуализация результатов
- Адаптивный дизайн

## Установка

### Бэкенд

1. Создайте виртуальное окружение:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Добавьте ваши Supabase ключи в `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

5. Запустите сервер:
```bash
uvicorn main:app --reload
```

### Фронтенд

1. Откройте `frontend/index.html` через локальный сервер (например, Live Server в VS Code)

## Использование

1. Откройте приложение в браузере
2. Загрузите CSV или Excel файл с данными о покупках
3. Выберите соответствующие столбцы:
   - ID клиента
   - Дата покупки
   - Сумма покупки
4. Нажмите "Загрузить"
5. После успешной загрузки нажмите "Запустить анализ"
6. Просмотрите результаты RFM-анализа

## Структура проекта

```
rfm-pro/
├── backend/
│   ├── main.py          # FastAPI приложение
│   ├── requirements.txt # Зависимости Python
│   └── .env             # Supabase ключи
├── frontend/
│   ├── index.html       # Главная страница
│   ├── components/      # Компоненты JS
│   │   ├── header.js
│   │   ├── upload.js
│   │   └── analysis.js
│   ├── styles.css       # Стили
│   └── app.js           # Главный скрипт
├── .gitignore           # Исключения для Git
└── README.md            # Инструкции
```

## Технологии

- Backend: Python, FastAPI
- Database: Supabase (PostgreSQL)
- Frontend: Web Components, Vanilla JavaScript
- Styling: CSS Variables, Flexbox, Grid

## Лицензия

MIT 