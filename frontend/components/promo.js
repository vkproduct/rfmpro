class PromoComponent extends HTMLElement {
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
                .pricing-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--spacing-lg);
                    margin-top: var(--spacing-xl);
                }
                .pricing-card {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .pricing-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                }
                .pricing-card.popular {
                    border: 2px solid var(--primary);
                }
                .popular-badge {
                    background: var(--primary);
                    color: white;
                    padding: 4px 12px;
                    border-radius: var(--radius);
                    font-size: 0.875rem;
                    font-weight: 500;
                    display: inline-block;
                    margin-bottom: var(--spacing-md);
                }
                .card-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--text);
                    margin-bottom: var(--spacing-sm);
                }
                .card-price {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: var(--spacing-md);
                    letter-spacing: -0.02em;
                }
                .card-price span {
                    font-size: 1rem;
                    color: var(--text-light);
                }
                .features-list {
                    list-style: none;
                    padding: 0;
                    margin: 0 0 var(--spacing-lg) 0;
                }
                .features-list li {
                    display: flex;
                    align-items: center;
                    margin-bottom: var(--spacing-sm);
                    color: var(--text-light);
                    font-size: 1.125rem;
                }
                .features-list li::before {
                    content: '✓';
                    color: var(--primary);
                    margin-right: var(--spacing-sm);
                }
                .button {
                    width: 100%;
                    padding: var(--spacing-md);
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
                    .pricing-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
            <div class="section-header">
                <h2>Тарифы</h2>
                <p>Выберите подходящий план для вашего бизнеса</p>
            </div>
            <div class="pricing-grid">
                <div class="pricing-card">
                    <div class="card-title">Базовый</div>
                    <div class="card-price">₽0<span>/месяц</span></div>
                    <ul class="features-list">
                        <li>До 1000 клиентов</li>
                        <li>Базовый RFM-анализ</li>
                        <li>CSV загрузка</li>
                        <li>Email поддержка</li>
                    </ul>
                    <button class="button primary">Начать бесплатно</button>
                </div>
                <div class="pricing-card popular">
                    <div class="popular-badge">Популярный</div>
                    <div class="card-title">Про</div>
                    <div class="card-price">₽2999<span>/месяц</span></div>
                    <ul class="features-list">
                        <li>До 10000 клиентов</li>
                        <li>Расширенный RFM-анализ</li>
                        <li>Excel загрузка</li>
                        <li>Приоритетная поддержка</li>
                        <li>API доступ</li>
                        <li>Экспорт отчетов</li>
                    </ul>
                    <button class="button primary">Выбрать план</button>
                </div>
                <div class="pricing-card">
                    <div class="card-title">Бизнес</div>
                    <div class="card-price">₽9999<span>/месяц</span></div>
                    <ul class="features-list">
                        <li>Безлимитное количество клиентов</li>
                        <li>Продвинутый RFM-анализ</li>
                        <li>Все форматы загрузки</li>
                        <li>24/7 поддержка</li>
                        <li>API доступ</li>
                        <li>Экспорт отчетов</li>
                        <li>Интеграции</li>
                        <li>Персональный менеджер</li>
                    </ul>
                    <button class="button primary">Связаться с нами</button>
                </div>
            </div>
        `;

        // Добавляем обработчики для кнопок
        const buttons = this.shadowRoot.querySelectorAll('.button');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                const plan = button.closest('.pricing-card').querySelector('.card-title').textContent;
                this.dispatchEvent(new CustomEvent('plan-selected', {
                    detail: { plan }
                }));
            });
        });
    }
}

customElements.define('promo-component', PromoComponent); 