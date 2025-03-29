class AnalysisComponent extends HTMLElement {
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
                .analysis-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--spacing-lg);
                    margin-top: var(--spacing-xl);
                }
                .analysis-card {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .analysis-card:hover {
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
                    grid-template-columns: repeat(3, 1fr);
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
                @media (max-width: 768px) {
                    .metrics-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
            <div class="section-header">
                <h2>Анализ данных</h2>
                <p>Получите подробный анализ вашей клиентской базы</p>
            </div>
            <div class="analysis-grid">
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-icon">📊</div>
                        <div class="card-title">RFM-метрики</div>
                    </div>
                    <div class="card-content">
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">4.2</div>
                                <div class="metric-label">Recency</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">3.8</div>
                                <div class="metric-label">Frequency</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">4.5</div>
                                <div class="metric-label">Monetary</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-icon">🎯</div>
                        <div class="card-title">Сегментация</div>
                    </div>
                    <div class="card-content">
                        <div class="chart-container">
                            <!-- Здесь будет график сегментации -->
                        </div>
                    </div>
                </div>
                <div class="analysis-card">
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
            <button class="button primary">Скачать отчет</button>
        `;

        // Здесь будет логика для загрузки и отображения данных
        this.loadData();
    }

    async loadData() {
        const token = localStorage.getItem('token');
        if (!token) {
            this.showError('Пожалуйста, войдите в систему');
            return;
        }

        try {
            const response = await fetch('/analyze', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Ошибка загрузки данных');
            }

            const data = await response.json();
            this.updateUI(data);
        } catch (error) {
            this.showError(error.message);
        }
    }

    updateUI(data) {
        // Обновление UI на основе полученных данных
        // Здесь будет код для обновления метрик и графиков
    }

    showError(message) {
        // Здесь будет код для отображения ошибки пользователю
    }
}

customElements.define('analysis-component', AnalysisComponent); 