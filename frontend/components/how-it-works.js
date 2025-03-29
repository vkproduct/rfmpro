class HowItWorksComponent extends HTMLElement {
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
                .steps-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--spacing-lg);
                    margin-top: var(--spacing-xl);
                }
                .step-card {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .step-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                }
                .step-number {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: var(--spacing-md);
                    letter-spacing: -0.02em;
                }
                .step-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--text);
                    margin-bottom: var(--spacing-md);
                    letter-spacing: -0.02em;
                }
                .step-description {
                    color: var(--text-light);
                    line-height: 1.6;
                    font-size: 1.125rem;
                }
                @media (max-width: 768px) {
                    .steps-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
            <div class="section-header">
                <h2>Как это работает</h2>
                <p>Простой процесс анализа вашей клиентской базы</p>
            </div>
            <div class="steps-grid">
                <div class="step-card">
                    <div class="step-number">01</div>
                    <h3 class="step-title">Загрузите данные</h3>
                    <p class="step-description">Выберите CSV или Excel файл с данными о покупках ваших клиентов</p>
                </div>
                <div class="step-card">
                    <div class="step-number">02</div>
                    <h3 class="step-title">Выберите столбцы</h3>
                    <p class="step-description">Укажите, какие столбцы содержат ID клиента, дату и сумму покупки</p>
                </div>
                <div class="step-card">
                    <div class="step-number">03</div>
                    <h3 class="step-title">Получите анализ</h3>
                    <p class="step-description">Система автоматически проанализирует данные и предоставит подробный отчет</p>
                </div>
            </div>
        `;
    }
}

customElements.define('how-it-works-component', HowItWorksComponent); 