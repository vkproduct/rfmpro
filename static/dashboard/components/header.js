/**
 * Компонент верхней панели и навигации
 */
const HeaderComponent = (function() {
    /**
     * Отрисовывает верхнюю панель
     * @returns {string} HTML верхней панели
     */
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
    
    /**
     * Отрисовывает вкладки навигации
     * @param {string} activeTab Активная вкладка
     * @returns {string} HTML вкладок
     */
    function renderTabs(activeTab) {
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
                        class="px-4 py-2 ${activeTab === tab.id ? 'bg-blue-100 text-blue-700 font-medium rounded-t' : ''}"
                        onclick="DashboardApp.changeTab('${tab.id}')"
                    >
                        ${tab.name}
                    </button>
                `).join('')}
            </div>
        `;
    }
    
    /**
     * Отрисовывает футер
     * @returns {string} HTML футера
     */
    function renderFooter() {
        return `
            <div class="bg-white p-4 border-t text-center text-sm text-gray-500">
                © 2025 RFM Pro - Система анализа клиентов | Версия 1.0 | Лицензия MIT
            </div>
        `;
    }
    
    // Публичный API
    return {
        renderHeader,
        renderTabs,
        renderFooter
    };
})();