/**
 * Сервис для работы с данными
 */
const DataService = (function() {
    // Демонстрационные данные для быстрого старта
    const DEMO_DATA = {
        summary: {
            total_customers: 24,
            total_revenue: 68420,
            avg_frequency: 2.3,
            avg_monetary: 2851
        },
        segments: {
            "Чемпионы": 5,
            "Лояльные клиенты": 7,
            "Новые клиенты": 4,
            "Под угрозой ухода": 3,
            "Потерянные": 5
        },
        rfm_scores: {
            "3": 2,
            "4": 4,
            "5": 3,
            "6": 5,
            "7": 4,
            "8": 3,
            "9": 2,
            "10": 1
        },
        customers: [
            {CustomerID: 1, Recency: 10, Frequency: 5, Monetary: 12500, RFM_Score: 8, Customer_Segment: "Чемпионы"},
            {CustomerID: 2, Recency: 45, Frequency: 2, Monetary: 4800, RFM_Score: 4, Customer_Segment: "Новые клиенты"},
            {CustomerID: 3, Recency: 5, Frequency: 8, Monetary: 18700, RFM_Score: 10, Customer_Segment: "Чемпионы"},
            {CustomerID: 4, Recency: 90, Frequency: 1, Monetary: 3200, RFM_Score: 3, Customer_Segment: "Потерянные"}
        ]
    };

    // API эндпоинты
    const API_ENDPOINTS = {
        RFM_DATA: '/api/rfm-data',
        UPLOAD_HISTORY: '/api/upload-history'
    };
    
    // Состояние данных
    let state = {
        rfmData: DEMO_DATA,
        uploadHistory: [],
        isLoading: false,
        error: null
    };
    
    // Обработчики событий при изменении данных
    const listeners = [];
    
    /**
     * Подписка на изменение данных
     * @param {Function} callback Функция-обработчик
     */
    function subscribe(callback) {
        listeners.push(callback);
        return () => {
            const index = listeners.indexOf(callback);
            if (index !== -1) {
                listeners.splice(index, 1);
            }
        };
    }
    
    /**
     * Оповещение всех слушателей об изменении данных
     */
    function notifyListeners() {
        listeners.forEach(listener => listener(state));
    }
    
    /**
     * Загрузка данных RFM-анализа
     * @returns {Promise} Промис с данными
     */
    async function loadRfmData() {
        try {
            const response = await fetch(API_ENDPOINTS.RFM_DATA);
            if (!response.ok) {
                throw new Error('Не удалось загрузить данные RFM');
            }
            
            const data = await response.json();
            if (data && data.summary && data.segments) {
                state.rfmData = data;
                notifyListeners();
                return data;
            } else {
                console.warn('Получены неполные данные RFM, используем демо-данные');
                return state.rfmData;
            }
        } catch (error) {
            console.error('Ошибка при загрузке данных RFM:', error);
            return state.rfmData;
        }
    }
    
    /**
     * Загрузка истории загрузок
     * @returns {Promise} Промис с данными истории
     */
    async function loadUploadHistory() {
        try {
            const response = await fetch(API_ENDPOINTS.UPLOAD_HISTORY);
            if (!response.ok) {
                throw new Error('Не удалось загрузить историю загрузок');
            }
            
            const data = await response.json();
            state.uploadHistory = data;
            notifyListeners();
            return data;
        } catch (error) {
            console.error('Ошибка при загрузке истории загрузок:', error);
            return [];
        }
    }
    
    /**
     * Экспорт данных в CSV
     */
    function exportToCSV() {
        if (!state.rfmData || !state.rfmData.customers || state.rfmData.customers.length === 0) {
            alert('Нет данных для экспорта');
            return;
        }
        
        const customers = state.rfmData.customers;
        
        // Получаем заголовки столбцов из первого клиента
        const headers = Object.keys(customers[0]);
        
        // Формируем строки CSV
        const csvRows = [
            headers.join(','), // Заголовок
            ...customers.map(customer => {
                return headers.map(header => {
                    // Обрабатываем значения, чтобы избежать проблем с запятыми и кавычками
                    const value = customer[header];
                    return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
                }).join(',');
            })
        ];
        
        // Объединяем строки в одну строку с переносами
        const csvString = csvRows.join('\n');
        
        // Создаем блоб и ссылку для скачивания
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'rfm_export.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    /**
     * Получение текущего состояния данных
     * @returns {Object} Текущее состояние
     */
    function getState() {
        return { ...state };
    }
    
    /**
     * Получение класса сегмента для стилизации
     * @param {string} segmentName Название сегмента
     * @returns {string} Класс сегмента
     */
    function getSegmentClass(segmentName) {
        const segmentMap = {
            'Чемпионы': 'champions',
            'Лояльные клиенты': 'loyal',
            'Потенциально лояльные': 'potential',
            'Новые клиенты': 'new',
            'Под угрозой ухода': 'risk',
            'Потерянные': 'lost'
        };
        
        return segmentMap[segmentName] || 'default';
    }
    
    // Загрузка данных при инициализации сервиса
    function init() {
        // Асинхронно загружаем данные
        loadRfmData();
        loadUploadHistory();
    }
    
    // Публичный API
    return {
        subscribe,
        getState,
        loadRfmData,
        loadUploadHistory,
        exportToCSV,
        getSegmentClass,
        init
    };
})();

// Инициализация сервиса данных
DataService.init();