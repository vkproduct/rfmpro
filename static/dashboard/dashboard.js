document.addEventListener('DOMContentLoaded', function() {
    console.log('Дашборд начинает загрузку...');
    
    // Демонстрационные данные для немедленного использования
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

    // Константы для работы с API
    const API_ENDPOINTS = {
        RFM_DATA: '/api/rfm-data',
        UPLOAD_HISTORY: '/api/upload-history'
    };
    
    // Состояние приложения
    let appState = {
        rfmData: DEMO_DATA, // Сразу используем демо-данные
        uploadHistory: [],
        isLoading: false,  // Сразу ставим false, чтобы отобразить интерфейс
        error: null,
        activeTab: 'overview'
    };
    
    // Выводим сообщение для диагностики
    console.log('Инициализация состояния приложения выполнена');
    
    // Функция для рендеринга верхней панели
    function renderHeader() {
        return `
            <div class="bg-blue-700 text-white shadow">
                <div class="container mx-auto px-4 py-3 flex justify-between items-center">
                    <h1 class="text-xl font-bold">RFM Pro - Расширенный дашборд</h1>
                    <div class="flex items-center space-x-4">
                        <button class="p-2 rounded hover:bg-blue-600" onclick="window.location.reload()">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38"/>
                            </svg>
                        </button>
                        <a href="/" class="hover:underline">
                            Вернуться на главную
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Функция для рендеринга вкладок
    function renderTabs() {
        const tabs = [
            { id: 'overview', name: 'Обзор' },
            { id: 'segments', name: 'Сегменты' },
            { id: 'clients', name: 'Клиенты' },
            { id: 'reports', name: 'Отчеты' }
        ];
        
        return `
            <div class="bg-white rounded-t border-b flex">
                ${tabs.map(tab => `
                    <button 
                        class="px-4 py-2 ${appState.activeTab === tab.id ? 'bg-blue-100 text-blue-700 font-medium rounded-t' : ''}"
                        onclick="changeTab('${tab.id}')"
                    >
                        ${tab.name}
                    </button>
                `).join('')}
            </div>
        `;
    }
    
    // Функция для рендеринга карточек с метриками
    function renderMetricCards() {
        if (!appState.rfmData || !appState.rfmData.summary) {
            return '<div class="text-center p-4">Нет данных для отображения</div>';
        }
        
        const { summary } = appState.rfmData;
        
        return `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-gray-500 text-sm mb-2">Всего клиентов</div>
                    <div class="text-2xl font-bold">${summary.total_customers}</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-gray-500 text-sm mb-2">Общая выручка</div>
                    <div class="text-2xl font-bold">₽${summary.total_revenue.toLocaleString()}</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-gray-500 text-sm mb-2">Средняя частота</div>
                    <div class="text-2xl font-bold">${summary.avg_frequency.toFixed(1)}</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-gray-500 text-sm mb-2">Средний чек</div>
                    <div class="text-2xl font-bold">₽${summary.avg_monetary.toLocaleString()}</div>
                </div>
            </div>
        `;
    }
    
    // Функция для рендеринга графиков
    function renderCharts() {
        if (!appState.rfmData || !appState.rfmData.segments) {
            return '<div class="text-center p-4">Нет данных для отображения графиков</div>';
        }
        
        return `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-lg shadow p-4">
                    <h3 class="text-lg font-semibold mb-4">Распределение по сегментам</h3>
                    <div class="chart-container" id="segments-chart"></div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <h3 class="text-lg font-semibold mb-4">Распределение по RFM-оценке</h3>
                    <div class="chart-container" id="rfm-scores-chart"></div>
                </div>
            </div>
        `;
    }
    
    // Функция для рендеринга таблицы клиентов
    function renderClientsTable() {
        if (!appState.rfmData || !appState.rfmData.customers || appState.rfmData.customers.length === 0) {
            return '<div class="text-center p-4">Нет данных о клиентах</div>';
        }
        
        const customers = appState.rfmData.customers.slice(0, 10); // Показываем только первые 10 для производительности
        
        return `
            <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
                <h3 class="text-lg font-semibold p-4 border-b">Данные по клиентам</h3>
                <div class="overflow-x-auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Recency</th>
                                <th>Frequency</th>
                                <th>Monetary</th>
                                <th>RFM Score</th>
                                <th>Сегмент</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${customers.map(customer => `
                                <tr>
                                    <td>${customer.CustomerID}</td>
                                    <td>${customer.Recency}</td>
                                    <td>${customer.Frequency}</td>
                                    <td>₽${customer.Monetary.toLocaleString()}</td>
                                    <td>${customer.RFM_Score}</td>
                                    <td>
                                        <span class="segment segment-${getSegmentClass(customer.Customer_Segment)}">
                                            ${customer.Customer_Segment}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="p-4 border-t text-right">
                    <span class="text-gray-500">Показаны первые 10 клиентов из ${appState.rfmData.customers.length}</span>
                </div>
            </div>
        `;
    }
    
    // Функция для рендеринга истории загрузок
    function renderUploadHistory() {
        if (!appState.uploadHistory || appState.uploadHistory.length === 0) {
            return '<div class="text-center p-4">История загрузок отсутствует</div>';
        }
        
        return `
            <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
                <h3 class="text-lg font-semibold p-4 border-b">История загрузок</h3>
                <div class="overflow-x-auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Дата</th>
                                <th>Файл</th>
                                <th>Кол-во записей</th>
                                <th>Сегментов</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${appState.uploadHistory.map(upload => `
                                <tr>
                                    <td>${upload.id}</td>
                                    <td>${upload.date}</td>
                                    <td>${upload.filename}</td>
                                    <td>${upload.records}</td>
                                    <td>${upload.segments}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    // Функция для получения класса сегмента
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
    
    // Функция для рендеринга контента текущей вкладки
    function renderTabContent() {
        switch (appState.activeTab) {
            case 'overview':
                return `
                    ${renderMetricCards()}
                    ${renderCharts()}
                `;
            case 'segments':
                return `
                    <div class="bg-white rounded-lg shadow p-6 mb-6">
                        <h3 class="text-lg font-semibold mb-4">Распределение клиентов по сегментам</h3>
                        <div id="segments-detail-chart" class="chart-container"></div>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                            ${appState.rfmData && appState.rfmData.segments ? 
                                Object.entries(appState.rfmData.segments).map(([segment, count]) => `
                                    <div class="p-4 border rounded">
                                        <h4 class="font-semibold mb-2">${segment}</h4>
                                        <div class="flex justify-between">
                                            <span>Количество клиентов:</span>
                                            <span class="font-bold">${count}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>% от общего:</span>
                                            <span class="font-bold">${((count / appState.rfmData.summary.total_customers) * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                `).join('') : 
                                '<div class="text-center">Нет данных о сегментах</div>'
                            }
                        </div>
                    </div>
                `;
            case 'clients':
                return renderClientsTable();
            case 'reports':
                return `
                    ${renderUploadHistory()}
                    <div class="bg-white rounded-lg shadow p-6 mb-6">
                        <h3 class="text-lg font-semibold mb-4">Экспорт отчетов</h3>
                        <div class="export-buttons mb-6">
                            <button class="btn btn-primary" onclick="exportToCSV()">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                    <polyline points="7 10 12 15 17 10"/>
                                    <line x1="12" y1="15" x2="12" y2="3"/>
                                </svg>
                                Экспорт в CSV
                            </button>
                            <button class="btn btn-danger" onclick="exportToPDF()">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                    <polyline points="14 2 14 8 20 8"/>
                                    <line x1="16" y1="13" x2="8" y2="13"/>
                                    <line x1="16" y1="17" x2="8" y2="17"/>
                                    <line x1="10" y1="9" x2="8" y2="9"/>
                                </svg>
                                Экспорт в PDF
                            </button>
                        </div>
                        <div class="text-gray-500 text-sm">
                            Для генерации детального отчета выберите необходимый формат экспорта.
                        </div>
                    </div>
                `;
            default:
                return '<div class="text-center p-4">Выберите вкладку</div>';
        }
    }
    
    // Функция для рендеринга всего дашборда
    function renderDashboard() {
        console.log('Рендеринг дашборда...');
        const root = document.getElementById('root');
        
        if (!root) {
            console.error('Корневой элемент #root не найден');
            return;
        }
        
        // Если данные загружаются, показываем индикатор загрузки
        if (appState.isLoading) {
            root.innerHTML = `
                <div class="flex items-center justify-center min-h-screen">
                    <div class="text-center">
                        <div class="loading-spinner mb-4"></div>
                        <h3 class="text-lg font-bold">Загрузка дашборда...</h3>
                    </div>
                </div>
            `;
            return;
        }
        
        // Если произошла ошибка, показываем сообщение об ошибке
        if (appState.error) {
            root.innerHTML = `
                <div class="flex flex-col h-screen">
                    ${renderHeader()}
                    <div class="flex items-center justify-center flex-grow">
                        <div class="bg-white rounded-lg shadow p-6 max-w-md">
                            <h2 class="text-red-500 text-lg font-bold mb-2">Ошибка</h2>
                            <p class="text-gray-600 mb-4">${appState.error}</p>
                            <button 
                                onclick="window.location.reload()" 
                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                Попробовать снова
                            </button>
                        </div>
                    </div>
                </div>
            `;
            return;
        }
        
        // Рендерим основной интерфейс
        root.innerHTML = `
            <div class="flex flex-col min-h-screen">
                ${renderHeader()}
                <div class="container mx-auto px-4 py-6 flex-grow">
                    ${renderTabs()}
                    <div class="py-6">
                        ${renderTabContent()}
                    </div>
                </div>
                <div class="bg-white p-4 border-t text-center text-sm text-gray-500">
                    © 2025 RFM Pro - Система анализа клиентов | Версия 1.0 | Лицензия MIT
                </div>
            </div>
        `;
        
        console.log('Дашборд отрендерен, инициализация графиков...');
        
        // Инициализируем графики, только если мы на соответствующих вкладках
        if (appState.activeTab === 'overview' || appState.activeTab === 'segments') {
            try {
                createFallbackCharts(); // Всегда используем запасные графики для надежности
                console.log('Графики инициализированы');
            } catch (error) {
                console.error('Ошибка при инициализации графиков:', error);
            }
        }
    }
    
    // Упрощенная функция создания графиков - всегда используем Canvas
    function createFallbackCharts() {
        console.log('Создание графиков на Canvas...');
        
        if (!appState.rfmData || !appState.rfmData.segments) {
            console.warn('Нет данных для графиков');
            return;
        }
        
        // Создаем простые графики на Canvas для сегментов
        const segmentData = Object.entries(appState.rfmData.segments).map(([name, count]) => ({
            name,
            value: count
        }));
        
        // Отображаем график сегментов
        if (document.getElementById('segments-chart')) {
            drawSimpleBarChart('segments-chart', segmentData);
        }
        
        // Отображаем график RFM Score, если данные доступны
        if (document.getElementById('rfm-scores-chart') && appState.rfmData.rfm_scores) {
            const rfmScoreData = Object.entries(appState.rfmData.rfm_scores)
                .map(([score, count]) => ({ name: score, value: count }))
                .sort((a, b) => parseInt(a.name) - parseInt(b.name));
                
            drawSimpleLineChart('rfm-scores-chart', rfmScoreData);
        }
        
        // Отображаем детальный график сегментов на вкладке Segments
        if (document.getElementById('segments-detail-chart')) {
            drawSimplePieChart('segments-detail-chart', segmentData);
        }
    }
    
    // Функция для рисования простой столбчатой диаграммы на Canvas
    function drawSimpleBarChart(containerId, data) {
        console.log(`Рисование столбчатой диаграммы в ${containerId}...`);
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return;
        }
        
        // Очищаем контейнер
        container.innerHTML = '';
        
        // Создаем canvas
        const canvas = document.createElement('canvas');
        canvas.width = container.clientWidth || 300;
        canvas.height = container.clientHeight || 200;
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        // Рисуем простую столбчатую диаграмму
        const barWidth = Math.min(50, (canvas.width - 60) / data.length - 10);
        const maxValue = Math.max(...data.map(item => item.value));
        
        // Рисуем оси
        ctx.beginPath();
        ctx.moveTo(40, 20);
        ctx.lineTo(40, canvas.height - 40);
        ctx.lineTo(canvas.width - 20, canvas.height - 40);
        ctx.stroke();
        
        // Рисуем столбцы
        data.forEach((item, index) => {
            const x = 50 + index * (barWidth + 10);
            const barHeight = (item.value / maxValue) * (canvas.height - 80);
            
            // Рисуем столбец
            ctx.fillStyle = '#4f46e5';
            ctx.fillRect(x, canvas.height - 40 - barHeight, barWidth, barHeight);
            
            // Добавляем подпись
            ctx.fillStyle = '#000';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(item.name.substring(0, 10), x + barWidth/2, canvas.height - 20);
            ctx.fillText(item.value, x + barWidth/2, canvas.height - 50 - barHeight);
        });
        
        // Добавляем заголовок
        ctx.fillStyle = '#000';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Распределение по сегментам', canvas.width / 2, 15);
        
        console.log(`Столбчатая диаграмма в ${containerId} нарисована`);
    }
    
    // Функция для рисования простой линейной диаграммы
    function drawSimpleLineChart(containerId, data) {
        console.log(`Рисование линейной диаграммы в ${containerId}...`);
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return;
        }
        
        container.innerHTML = '';
        
        const canvas = document.createElement('canvas');
        canvas.width = container.clientWidth || 300;
        canvas.height = container.clientHeight || 200;
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        // Настройки
        const padding = { top: 20, right: 20, bottom: 40, left: 40 };
        const chartWidth = canvas.width - padding.left - padding.right;
        const chartHeight = canvas.height - padding.top - padding.bottom;
        
        // Находим максимальное значение
        const maxValue = Math.max(...data.map(item => item.value));
        
        // Рисуем оси
        ctx.beginPath();
        ctx.moveTo(padding.left, padding.top);
        ctx.lineTo(padding.left, canvas.height - padding.bottom);
        ctx.lineTo(canvas.width - padding.right, canvas.height - padding.bottom);
        ctx.stroke();
        
        if (data.length > 1) {
            // Рисуем линию графика
            ctx.beginPath();
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            
            data.forEach((item, index) => {
                const x = padding.left + (index / (data.length - 1)) * chartWidth;
                const y = canvas.height - padding.bottom - ((item.value / maxValue) * chartHeight);
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Рисуем точки
            data.forEach((item, index) => {
                const x = padding.left + (index / (data.length - 1)) * chartWidth;
                const y = canvas.height - padding.bottom - ((item.value / maxValue) * chartHeight);
                
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, Math.PI * 2);
                ctx.fillStyle = '#3b82f6';
                ctx.fill();
                
                // Подписи к точкам
                ctx.fillStyle = '#000';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(item.name, x, canvas.height - padding.bottom + 15);
                ctx.fillText(item.value, x, y - 10);
            });
        } else if (data.length === 1) {
            // Если только одна точка данных
            const x = canvas.width / 2;
            const y = canvas.height - padding.bottom - ((data[0].value / maxValue) * chartHeight);
            
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fillStyle = '#3b82f6';
            ctx.fill();
            
            ctx.fillStyle = '#000';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(data[0].name, x, canvas.height - padding.bottom + 15);
            ctx.fillText(data[0].value, x, y - 10);
        }
        
        // Заголовок
        ctx.fillStyle = '#000';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Распределение по RFM-оценке', canvas.width / 2, 15);
        
        console.log(`Линейная диаграмма в ${containerId} нарисована`);
    }
    
    // Функция для рисования круговой диаграммы
    function drawSimplePieChart(containerId, data) {
        console.log(`Рисование круговой диаграммы в ${containerId}...`);
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return;
        }
        
        container.innerHTML = '';
        
        const canvas = document.createElement('canvas');
        canvas.width = container.clientWidth || 300;
        canvas.height = container.clientHeight || 200;
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        // Расчет общего значения
        const total = data.reduce((sum, item) => sum + item.value, 0);
        
        // Центр и радиус
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 30;
        
        // Цвета для сегментов
        const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280'];
        
        // Рисуем сегменты
        let startAngle = 0;
        
        // Рисуем легенду
        const legendY = canvas.height - 20;
        let legendX = 50;
        
        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * 2 * Math.PI;
            
            // Рисуем сегмент
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            
            const color = colors[index % colors.length];
            ctx.fillStyle = color;
            ctx.fill();
            
            // Рисуем легенду
            ctx.fillStyle = color;
            ctx.fillRect(legendX, legendY, 10, 10);
            
            ctx.fillStyle = '#000';
            ctx.font = '12px Arial';
            ctx.textAlign = 'left';
            const label = `${item.name} (${Math.round((item.value / total) * 100)}%)`;
            ctx.fillText(label, legendX + 15, legendY + 9);
            
            legendX += ctx.measureText(label).width + 30;
            if (legendX > canvas.width - 50) {
                legendX = 50;
                legendY -= 20;
            }
            
            startAngle += sliceAngle;
        });
        
        // Заголовок
        ctx.fillStyle = '#000';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Распределение клиентов по сегментам', canvas.width / 2, 15);
        
        console.log(`Круговая диаграмма в ${containerId} нарисована`);
    }
    
    // Глобальная функция для переключения вкладок
    window.changeTab = function(tabId) {
        console.log(`Переключение на вкладку ${tabId}`);
        appState.activeTab = tabId;
        renderDashboard();
    };
    
    // Глобальная функция для экспорта данных в CSV
    window.exportToCSV = function() {
        console.log('Экспорт в CSV...');
        if (!appState.rfmData || !appState.rfmData.customers) {
            alert('Нет данных для экспорта');
            return;
        }
        
        const customers = appState.rfmData.customers;
        
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
        
        console.log('Экспорт в CSV выполнен');
    };
    
    // Глобальная функция для экспорта в PDF
    window.exportToPDF = function() {
        alert('Функция экспорта в PDF будет доступна в следующем обновлении');
    };
    
    // Запускаем рендеринг дашборда сразу, используя демо-данные
    console.log('Запуск рендеринга дашборда...');
    renderDashboard();
    
    // Затем пытаемся загрузить реальные данные асинхронно
    console.log('Запуск асинхронной загрузки данных...');
    
    // Загружаем историю загрузок в фоновом режиме
    fetch(API_ENDPOINTS.UPLOAD_HISTORY)
        .then(response => response.json())
        .then(data => {
            console.log('История загрузок загружена:', data);
            appState.uploadHistory = data;
            // Обновляем только если мы на вкладке "Отчеты"
            if (appState.activeTab === 'reports') {
                renderDashboard();
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке истории загрузок:', error);
        });
    
    // Загружаем данные RFM-анализа в фоновом режиме
    fetch(API_ENDPOINTS.RFM_DATA)
        .then(response => response.json())
        .then(data => {
            console.log('Данные RFM загружены:', data);
            // Проверяем, что данные имеют правильную структуру
            if (data && data.summary && data.segments) {
                appState.rfmData = data;
                renderDashboard(); // Обновляем дашборд с новыми данными
            } else {
                console.warn('Получены неполные данные RFM, используем демо-данные');
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных RFM:', error);
        });
});