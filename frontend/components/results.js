class ResultsComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                }
                .section-header {
                    text-align: center;
                    margin-bottom: var(--spacing-xl);
                }
                .section-header h2 {
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: var(--spacing-md);
                    letter-spacing: -0.02em;
                }
                .section-header p {
                    font-size: 1.5rem;
                    color: var(--text-light);
                    max-width: 600px;
                    margin: 0 auto;
                    line-height: 1.4;
                }
                .results-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--spacing-lg);
                    margin-top: var(--spacing-xl);
                }
                .result-card {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .result-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                }
                .card-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: var(--spacing-md);
                }
                .card-icon {
                    font-size: 2rem;
                    margin-right: var(--spacing-md);
                    color: var(--primary);
                }
                .card-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--text);
                    letter-spacing: -0.02em;
                }
                .card-content {
                    color: var(--text-light);
                    line-height: 1.6;
                    font-size: 1.125rem;
                }
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: var(--spacing-md);
                    margin-top: var(--spacing-lg);
                }
                .metric-card {
                    background: var(--background-alt);
                    padding: var(--spacing-md);
                    border-radius: var(--radius);
                    text-align: center;
                    transition: all 0.2s ease;
                }
                .metric-card:hover {
                    transform: translateY(-1px);
                    box-shadow: var(--shadow);
                }
                .metric-value {
                    font-size: 2rem;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: var(--spacing-xs);
                    letter-spacing: -0.02em;
                }
                .metric-label {
                    font-size: 1rem;
                    color: var(--text-light);
                }
                .chart-container {
                    margin-top: var(--spacing-lg);
                    height: 300px;
                    background: var(--background-alt);
                    border-radius: var(--radius);
                    padding: var(--spacing-md);
                    transition: all 0.2s ease;
                }
                .chart-container:hover {
                    box-shadow: var(--shadow);
                }
                .button {
                    width: 100%;
                    padding: var(--spacing-md);
                    margin-top: var(--spacing-lg);
                    font-size: 1.125rem;
                }
                .button.primary {
                    background: var(--primary);
                    color: white;
                    border: none;
                }
                .button.primary:hover {
                    background: var(--primary-hover);
                    transform: translateY(-1px);
                }
                .table-container {
                    margin-top: var(--spacing-lg);
                    overflow-x: auto;
                    border-radius: var(--radius);
                    box-shadow: var(--shadow);
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background: var(--background);
                }
                th, td {
                    padding: var(--spacing-md);
                    text-align: left;
                    border-bottom: 1px solid var(--border);
                }
                th {
                    background: var(--background-alt);
                    font-weight: 600;
                    color: var(--text);
                    font-size: 1.125rem;
                }
                td {
                    color: var(--text-light);
                    font-size: 1.125rem;
                }
                tr:hover {
                    background: var(--background-alt);
                }
                @media (max-width: 768px) {
                    .metrics-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
            <div class="section-header">
                <h2>Результаты анализа</h2>
                <p>Подробная информация о вашей клиентской базе</p>
            </div>
            <div class="results-grid">
                <div class="result-card">
                    <div class="card-header">
                        <div class="card-icon">📊</div>
                        <div class="card-title">Общая статистика</div>
                    </div>
                    <div class="card-content">
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">1,234</div>
                                <div class="metric-label">Всего клиентов</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">4.2</div>
                                <div class="metric-label">Средний RFM</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="result-card">
                    <div class="card-header">
                        <div class="card-icon">🎯</div>
                        <div class="card-title">Сегменты</div>
                    </div>
                    <div class="card-content">
                        <div class="chart-container">
                            <!-- Здесь будет график сегментов -->
                        </div>
                    </div>
                </div>
                <div class="result-card">
                    <div class="card-header">
                        <div class="card-icon">📈</div>
                        <div class="card-title">Тренды</div>
                    </div>
                    <div class="card-content">
                        <div class="chart-container">
                            <!-- Здесь будет график трендов -->
                        </div>
                    </div>
                </div>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID клиента</th>
                            <th>Recency</th>
                            <th>Frequency</th>
                            <th>Monetary</th>
                            <th>RFM Score</th>
                            <th>Сегмент</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Здесь будут данные таблицы -->
                    </tbody>
                </table>
            </div>
            <button class="button primary">Скачать отчет</button>
        `;

        // Здесь будет логика для загрузки и отображения данных
        this.loadData();
    }

    async loadData() {
        try {
            const response = await fetch('http://localhost:8000/results');
            if (!response.ok) {
                throw new Error('Ошибка загрузки данных');
            }
            const data = await response.json();
            this.updateUI(data);
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    updateUI(data) {
        // Обновление UI на основе полученных данных
        // Здесь будет код для обновления метрик, графиков и таблицы
    }
}

customElements.define('results-component', ResultsComponent); 