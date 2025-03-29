# RFM Анализ

Сервис для анализа клиентской базы с использованием RFM-методологии.

## Возможности

- Загрузка данных из CSV файлов
- RFM-анализ клиентов
- Визуализация результатов
- Экспорт отчетов

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/rfm-analysis.git
cd rfm-analysis
```

2. Установите зависимости для бэкенда:
```bash
cd backend
pip install -r requirements.txt
```

3. Запустите сервер:
```bash
python app.py
```

4. Откройте `frontend/index.html` в браузере

## Использование

1. Зарегистрируйтесь или войдите в систему
2. Загрузите CSV файл с данными транзакций
3. Укажите названия колонок с датами, суммами и ID клиентов
4. Получите результаты анализа

## Формат данных

CSV файл должен содержать следующие колонки:
- Дата транзакции
- Сумма транзакции
- ID клиента

## Лицензия

MIT 