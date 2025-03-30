/**
 * Компонент для отображения табличных данных
 */
const TablesComponent = (function() {
    /**
     * Отрисовывает таблицу клиентов
     * @returns {string} HTML таблицы клиентов
     */
    function renderClientsTable() {
        const state = DataService.getState();
        
        if (!state.rfmData || !state.rfmData.customers || state.rfmData.customers.length === 0) {
            return '<div class="text-center p-4">Нет данных о клиентах</div>';
        }
        
        const customers = state.rfmData.customers.slice(0, 10); // Показываем только первые 10 для производительности
        
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
                                        <span class="segment segment-${DataService.getSegmentClass(customer.Customer_Segment)}">
                                            ${customer.Customer_Segment}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="p-4 border-t text-right">
                    <span class="text-gray-500">Показаны первые 10 клиентов из ${state.rfmData.customers.length}</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Создает пагинацию для таблицы
     * @param {number} currentPage Текущая страница
     * @param {number} totalPages Всего страниц
     * @returns {string} HTML пагинации
     */
    function createPagination(currentPage, totalPages) {
        if (totalPages <= 1) {
            return '';
        }
        
        let paginationHtml = '<div class="pagination flex justify-center mt-4">';
        
        // Кнопка "Предыдущая"
        if (currentPage > 1) {
            paginationHtml += `<button class="pagination-btn" onclick="TablesComponent.goToPage(${currentPage - 1})">Предыдущая</button>`;
        } else {
            paginationHtml += '<button class="pagination-btn disabled" disabled>Предыдущая</button>';
        }
        
        // Номера страниц
        for (let i = 1; i <= totalPages; i++) {
            if (i === currentPage) {
                paginationHtml += `<button class="pagination-btn active">${i}</button>`;
            } else {
                paginationHtml += `<button class="pagination-btn" onclick="TablesComponent.goToPage(${i})">${i}</button>`;
            }
        }
        
        // Кнопка "Следующая"
        if (currentPage < totalPages) {
            paginationHtml += `<button class="pagination-btn" onclick="TablesComponent.goToPage(${currentPage + 1})">Следующая</button>`;
        } else {
            paginationHtml += '<button class="pagination-btn disabled" disabled>Следующая</button>';
        }
        
        paginationHtml += '</div>';
        
        return paginationHtml;
    }
    
    /**
     * Переход на указанную страницу
     * @param {number} page Номер страницы
     */
    function goToPage(page) {
        console.log(`Переход на страницу ${page}`);
        // Логика пагинации здесь
        // Обновляем отображение таблицы
        const tableContainer = document.getElementById('clients-table-container');
        if (tableContainer) {
            // Обновляем содержимое
        }
    }
    
    /**
     * Поиск в таблице клиентов
     * @param {string} query Поисковый запрос
     */
    function searchClients(query) {
        console.log(`Поиск клиентов: ${query}`);
        // Логика поиска
    }
    
    // Публичный API
    return {
        renderClientsTable,
        createPagination,
        goToPage,
        searchClients
    };
})();