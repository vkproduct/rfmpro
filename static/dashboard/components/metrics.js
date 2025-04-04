/**
 * Компонент для отображения метрик и графиков
 */
const MetricsComponent = (function() {
    /**
     * Отрисовывает карточки с метриками
     * @returns {string} HTML карточек с метриками
     */
    function renderMetricCards() {
        const state = DataService.getState();
        
        if (!state.rfmData || !state.rfmData.summary) {
            return '<div class="text-center p-4">Нет данных для отображения</div>';
        }
        
        const { summary } = state.rfmData;
        
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
    
    /**
     * Отрисовывает контейнеры для графиков обзорной страницы
     * @returns {string} HTML контейнеров для графиков
     */
    function renderChartContainers() {
        return `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-lg shadow p-4">
                    <h3 class="text-lg font-semibold mb-4">Распределение по сегментам</h3>
                    <div class="chart-container" id="segments-chart"></div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <h3 class="text-lg font-semibold mb-4">Доход по каждому сегменту</h3>
                    <div class="chart-container" id="segment-revenue-chart"></div>
                </div>
            </div>
        `;
    }
    
    /**
     * Отрисовывает содержимое вкладки "Обзор"
     * @returns {string} HTML содержимого вкладки
     */
    function renderOverviewTab() {
        return `
            ${renderMetricCards()}
            ${renderChartContainers()}
        `;
    }
    
    // Публичный API
    return {
        renderMetricCards,
        renderChartContainers,
        renderOverviewTab
    };
})();