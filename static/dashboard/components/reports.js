/**
 * Компонент для работы с отчетами и историей загрузок
 */
const ReportsComponent = (function() {
    /**
     * Отрисовывает таблицу истории загрузок
     * @returns {string} HTML таблицы истории загрузок
     */
    function renderUploadHistory() {
        const state = DataService.getState();
        
        if (!state.uploadHistory || state.uploadHistory.length === 0) {
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
                            ${state.uploadHistory.map(upload => `
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
    
    /**
     * Отрисовывает панель экспорта отчетов
     * @returns {string} HTML панели экспорта
     */
    function renderExportPanel() {
        return `
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Экспорт отчетов</h3>
                <div class="export-buttons mb-6">
                    <button class="btn btn-primary" onclick="DashboardApp.exportToCSV()">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        Экспорт в CSV
                    </button>
                    <button class="btn btn-danger" onclick="DashboardApp.exportToPDF()">
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
    }
    
    /**
     * Отрисовывает форму настройки периодических отчетов
     * @returns {string} HTML формы настройки отчетов
     */
    function renderSchedulePanel() {
        return `
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Запланировать отчет</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Тип отчета</label>
                        <select class="w-full p-2 border rounded" id="report-type">
                            <option value="rfm-analysis">Полный RFM-анализ</option>
                            <option value="segments">Отчет по сегментам</option>
                            <option value="clients">Список клиентов</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Периодичность</label>
                        <select class="w-full p-2 border rounded" id="report-frequency">
                            <option value="daily">Ежедневно</option>
                            <option value="weekly">Еженедельно</option>
                            <option value="monthly">Ежемесячно</option>
                        </select>
                    </div>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email для отправки</label>
                    <input type="email" class="w-full p-2 border rounded" id="report-email" placeholder="email@example.com">
                </div>
                <div class="text-right">
                    <button class="btn btn-primary" onclick="ReportsComponent.scheduleReport()">
                        Запланировать отчет
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Планирование отчета (заглушка)
     */
    function scheduleReport() {
        const reportType = document.getElementById('report-type').value;
        const frequency = document.getElementById('report-frequency').value;
        const email = document.getElementById('report-email').value;
        
        if (!email) {
            alert('Пожалуйста, укажите email для отправки отчета');
            return;
        }
        
        alert(`Отчет "${reportType}" будет отправляться на ${email} с периодичностью: ${frequency}`);
    }
    
    /**
     * Отрисовывает полную вкладку отчетов
     * @returns {string} HTML вкладки отчетов
     */
    function renderReportsTab() {
        return `
            ${renderUploadHistory()}
            ${renderExportPanel()}
            ${renderSchedulePanel()}
        `;
    }
    
    // Публичный API
    return {
        renderUploadHistory,
        renderExportPanel,
        renderSchedulePanel,
        renderReportsTab,
        scheduleReport
    };
})();