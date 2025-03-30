/**
 * Компонент для работы с сегментами клиентов
 */
const SegmentsComponent = (function() {
    /**
     * Отрисовывает контейнер для детального графика сегментов
     * @returns {string} HTML контейнера для графика
     */
    function renderSegmentChartContainer() {
        return `
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Распределение клиентов по сегментам</h3>
                <div id="segments-detail-chart" class="chart-container"></div>
            </div>
        `;
    }
    
    /**
     * Отрисовывает карточки с информацией о сегментах
     * @returns {string} HTML карточек сегментов
     */
    function renderSegmentCards() {
        const state = DataService.getState();
        
        if (!state.rfmData || !state.rfmData.segments) {
            return '<div class="text-center p-4">Нет данных о сегментах</div>';
        }
        
        const segmentColors = {
            'Чемпионы': 'bg-indigo-100 border-indigo-500',
            'Лояльные клиенты': 'bg-blue-100 border-blue-500',
            'Потенциально лояльные': 'bg-green-100 border-green-500',
            'Новые клиенты': 'bg-purple-100 border-purple-500',
            'Под угрозой ухода': 'bg-yellow-100 border-yellow-500',
            'Нельзя потерять': 'bg-orange-100 border-orange-500',
            'Потерянные': 'bg-red-100 border-red-500',
            'Крупные покупатели': 'bg-teal-100 border-teal-500'
        };
        
        return `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                ${Object.entries(state.rfmData.segments).map(([segment, count]) => `
                    <div class="p-4 border-l-4 rounded shadow ${segmentColors[segment] || 'bg-gray-100 border-gray-500'}">
                        <h4 class="font-semibold mb-2">${segment}</h4>
                        <div class="flex justify-between">
                            <span>Количество клиентов:</span>
                            <span class="font-bold">${count}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>% от общего:</span>
                            <span class="font-bold">${((count / state.rfmData.summary.total_customers) * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    /**
     * Отрисовывает рекомендации по работе с сегментами
     * @returns {string} HTML рекомендаций
     */
    function renderSegmentRecommendations() {
        const recommendations = {
            'Чемпионы': 'Работайте над лояльностью, предлагайте эксклюзивные продукты. Они ваши лучшие клиенты и амбассадоры.',
            'Лояльные клиенты': 'Увеличивайте средний чек, предлагайте кросс-продажи и больше внимания.',
            'Потенциально лояльные': 'Работайте над увеличением частоты покупок, стимулируйте повторные продажи.',
            'Новые клиенты': 'Улучшайте клиентский опыт, предлагайте программы лояльности.',
            'Под угрозой ухода': 'Срочная реактивация. Спецпредложения и персональные контакты.',
            'Нельзя потерять': 'Разработайте специальную программу удержания, выясните причины снижения активности.',
            'Потерянные': 'Оцените потенциал возврата. Агрессивные спецпредложения для реактивации.',
            'Крупные покупатели': 'Стимулируйте к более частым покупкам, используйте высокий средний чек.'
        };
        
        return `
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Рекомендации по работе с сегментами</h3>
                <div class="space-y-4">
                    ${Object.entries(recommendations).map(([segment, recommendation]) => `
                        <div class="p-4 bg-gray-50 rounded">
                            <h4 class="font-medium text-blue-700">${segment}</h4>
                            <p class="mt-1 text-gray-600">${recommendation}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    /**
     * Отрисовывает полную вкладку сегментов
     * @returns {string} HTML вкладки сегментов
     */
    function renderSegmentsTab() {
        return `
            ${renderSegmentChartContainer()}
            ${renderSegmentCards()}
            ${renderSegmentRecommendations()}
        `;
    }
    
    /**
     * Экспорт сегментов в CSV
     */
    function exportSegmentsToCSV() {
        const state = DataService.getState();
        
        if (!state.rfmData || !state.rfmData.segments) {
            alert('Нет данных для экспорта');
            return;
        }
        
        const headers = ['Сегмент', 'Количество клиентов', 'Процент от общего'];
        const rows = Object.entries(state.rfmData.segments).map(([segment, count]) => [
            segment,
            count,
            ((count / state.rfmData.summary.total_customers) * 100).toFixed(1) + '%'
        ]);
        
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'segments_report.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Публичный API
    return {
        renderSegmentChartContainer,
        renderSegmentCards,
        renderSegmentRecommendations,
        renderSegmentsTab,
        exportSegmentsToCSV
    };
})();