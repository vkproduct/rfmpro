class UseCasesComponent extends HTMLElement {
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
                .cases-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--spacing-lg);
                    margin-top: var(--spacing-xl);
                }
                .case-card {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .case-card:hover {
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
                .benefits-list {
                    margin-top: var(--spacing-md);
                    padding-left: var(--spacing-md);
                }
                .benefits-list li {
                    margin-bottom: var(--spacing-sm);
                    color: var(--text-light);
                    font-size: 1.125rem;
                }
                .benefits-list li::marker {
                    color: var(--primary);
                }
                @media (max-width: 768px) {
                    .cases-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
            <div class="section-header">
                <h2>Кейсы использования</h2>
                <p>Применение RFM-анализа в различных сферах бизнеса</p>
            </div>
            <div class="cases-grid">
                <div class="case-card">
                    <div class="card-header">
                        <div class="card-icon">🎯</div>
                        <div class="card-title">Таргетированный маркетинг</div>
                    </div>
                    <div class="card-content">
                        <p>Используйте RFM-анализ для создания персонализированных маркетинговых кампаний</p>
                        <ul class="benefits-list">
                            <li>Сегментация по ценностным группам</li>
                            <li>Оптимизация маркетингового бюджета</li>
                            <li>Увеличение конверсии</li>
                        </ul>
                    </div>
                </div>
                <div class="case-card">
                    <div class="card-header">
                        <div class="card-icon">💎</div>
                        <div class="card-title">Управление лояльностью</div>
                    </div>
                    <div class="card-content">
                        <p>Выявляйте ценных клиентов и разрабатывайте программы лояльности</p>
                        <ul class="benefits-list">
                            <li>Идентификация VIP-клиентов</li>
                            <li>Предотвращение оттока</li>
                            <li>Увеличение LTV</li>
                        </ul>
                    </div>
                </div>
                <div class="case-card">
                    <div class="card-header">
                        <div class="card-icon">📈</div>
                        <div class="card-title">Прогнозирование продаж</div>
                    </div>
                    <div class="card-content">
                        <p>Прогнозируйте будущие продажи на основе исторических данных</p>
                        <ul class="benefits-list">
                            <li>Точное планирование</li>
                            <li>Оптимизация запасов</li>
                            <li>Управление ресурсами</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
}

customElements.define('use-cases-component', UseCasesComponent); 