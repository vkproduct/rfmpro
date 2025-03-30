/**
 * Главное приложение дашборда RFM Pro
 */
const DashboardApp = (function() {
    // Активная вкладка
    let activeTab = 'overview';
    
    /**
     * Инициализация приложения
     */
    function init() {
        console.log('Инициализация приложения дашборда...');
        
        // Подписываемся на изменения данных
        DataService.subscribe(function() {
            renderDashboard();
        });
        
        // Первичная отрисовка дашборда
        renderDashboard();
    }
    
    /**
     * Отрисовка всего дашборда
     */
    function renderDashboard() {
        console.log('Отрисовка дашборда...');
        const root = document.getElementById('root');
        
        if (!root) {
            console.error('Корневой элемент #root не найден');
            return;
        }
        
        const state = DataService.getState();
        
        // Если данные загружаются, показываем индикатор загрузки
        if (state.isLoading) {
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
        if (state.error) {
            root.innerHTML = `
                <div class="flex flex-col h-screen">
                    ${HeaderComponent.renderHeader()}
                    <div class="flex items-center justify-center flex-grow">
                        <div class="bg-white rounded-lg shadow p-6 max-w-md">
                            <h2 class="text-red-500 text-lg font-bold mb-2">Ошибка</h2>
                            <p class="text-gray-600 mb-4">${state.error}</p>
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
                ${HeaderComponent.renderHeader()}
                <div class="container mx-auto px-4 py-6 flex-grow">
                    ${HeaderComponent.renderTabs(activeTab)}
                    <div class="py-6">
                        ${renderTabContent()}
                    </div>
                </div>
                ${HeaderComponent.renderFooter()}
            </div>
        `;
        
        // Инициализируем графики, если необходимо
        if (activeTab === 'overview' || activeTab === 'segments') {
            try {
                ChartUtils.initializeCharts(activeTab);
            } catch (error) {
                console.error('Ошибка при инициализации графиков:', error);
            }
        }
    }
    
    /**
     * Отрисовка содержимого активной вкладки
     * @returns {string} HTML содержимого вкладки
     */
    function renderTabContent() {
        switch (activeTab) {
            case 'overview':
                return MetricsComponent.renderOverviewTab();
            case 'segments':
                return SegmentsComponent.renderSegmentsTab();
            case 'clients':
                return TablesComponent.renderClientsTable();
            case 'reports':
                return ReportsComponent.renderReportsTab();
            default:
                return '<div class="text-center p-4">Выберите вкладку</div>';
        }
    }
    
    /**
     * Изменение активной вкладки
     * @param {string} tabId Идентификатор вкладки
     */
    function changeTab(tabId) {
        console.log(`Переключение на вкладку ${tabId}`);
        activeTab = tabId;
        renderDashboard();
    }
    
    /**
     * Экспорт данных в CSV
     */
    function exportToCSV() {
        DataService.exportToCSV();
    }
    
    /**
     * Экспорт в PDF
     */
    function exportToPDF() {
        alert('Функция экспорта в PDF будет доступна в следующем обновлении');
    }
    
    // Публичный API
    return {
        init,
        changeTab,
        exportToCSV,
        exportToPDF
    };
})();

// Инициализация приложения при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    DashboardApp.init();
});