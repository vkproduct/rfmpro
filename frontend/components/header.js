class HeaderComponent extends HTMLElement {
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
                header {
                    background: var(--background);
                    border-bottom: 1px solid var(--border);
                    padding: var(--spacing-md) 0;
                    position: sticky;
                    top: 0;
                    z-index: 100;
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                }
                .header-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 var(--spacing-md);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .logo {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--text);
                    text-decoration: none;
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-sm);
                    letter-spacing: -0.02em;
                }
                .logo-icon {
                    font-size: 1.75rem;
                    color: var(--primary);
                }
                .nav {
                    display: flex;
                    gap: var(--spacing-lg);
                    align-items: center;
                }
                .nav-link {
                    color: var(--text-light);
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.2s ease;
                    font-size: 1.125rem;
                }
                .nav-link:hover {
                    color: var(--primary);
                }
                .nav-link.active {
                    color: var(--primary);
                }
                .button {
                    padding: var(--spacing-sm) var(--spacing-md);
                    border-radius: var(--radius);
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
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
                .button.secondary {
                    background: transparent;
                    color: var(--text);
                    border: 2px solid var(--border);
                }
                .button.secondary:hover {
                    border-color: var(--primary);
                    color: var(--primary);
                    transform: translateY(-1px);
                }
                .burger-menu {
                    display: none;
                    font-size: 1.5rem;
                    color: var(--text);
                    cursor: pointer;
                }
                .modal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    align-items: center;
                    justify-content: center;
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                }
                .modal.active {
                    display: flex;
                }
                .modal-content {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    max-width: 1200px;
                    width: 90%;
                    max-height: 70vh;
                    position: relative;
                    box-shadow: var(--shadow-lg);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }
                .modal-close {
                    position: absolute;
                    top: var(--spacing-md);
                    right: var(--spacing-md);
                    font-size: 1.5rem;
                    color: var(--text-light);
                    cursor: pointer;
                    transition: color 0.2s ease;
                }
                .modal-close:hover {
                    color: var(--text);
                }
                .modal-title {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--text);
                    margin-bottom: var(--spacing-md);
                    letter-spacing: -0.02em;
                }
                .pricing-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: var(--spacing-md);
                    margin-top: var(--spacing-md);
                    margin-bottom: var(--spacing-md);
                }
                .pricing-card {
                    background: var(--background);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-md);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                    display: flex;
                    flex-direction: column;
                    height: fit-content;
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
                    font-size: 1.125rem;
                    font-weight: 600;
                    color: var(--text);
                    margin-bottom: var(--spacing-xs);
                }
                .card-price {
                    font-size: 1.75rem;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: var(--spacing-xs);
                    letter-spacing: -0.02em;
                }
                .card-price span {
                    font-size: 1rem;
                    color: var(--text-light);
                }
                .features-list {
                    list-style: none;
                    padding: 0;
                    margin: 0 0 var(--spacing-sm) 0;
                }
                .features-list li {
                    display: flex;
                    align-items: center;
                    margin-bottom: var(--spacing-xs);
                    color: var(--text-light);
                    font-size: 0.875rem;
                }
                .features-list li::before {
                    content: '✓';
                    color: var(--primary);
                    margin-right: var(--spacing-sm);
                }
                .button {
                    padding: var(--spacing-xs) var(--spacing-sm);
                    font-size: 0.875rem;
                }
                @media (max-width: 768px) {
                    .nav {
                        display: none;
                    }
                    .burger-menu {
                        display: block;
                    }
                    .nav.active {
                        display: flex;
                        flex-direction: column;
                        position: absolute;
                        top: 100%;
                        left: 0;
                        right: 0;
                        background: var(--background);
                        padding: var(--spacing-md);
                        border-bottom: 1px solid var(--border);
                        box-shadow: var(--shadow);
                    }
                    .pricing-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
            <header>
                <div class="header-content">
                    <a href="/" class="logo">
                        <span class="logo-icon">📊</span>
                        <span>RFM Pro</span>
                    </a>
                    <nav class="nav">
                        <a href="#features" class="nav-link">Возможности</a>
                        <a href="#how-it-works" class="nav-link">Как это работает</a>
                        <a href="#pricing" class="nav-link">Тарифы</a>
                        <a href="#contact" class="nav-link">Контакты</a>
                        <button class="button secondary pricing-trigger">Тарифы</button>
                        <button class="button primary auth-trigger">Войти</button>
                    </nav>
                    <div class="burger-menu">☰</div>
                </div>
            </header>
            <div class="modal">
                <div class="modal-content">
                    <div class="modal-close">×</div>
                    <h2 class="modal-title">Выберите тариф</h2>
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
                </div>
            </div>
            <auth-component></auth-component>
        `;

        // Добавляем обработчики для мобильного меню
        const burgerMenu = this.shadowRoot.querySelector('.burger-menu');
        const nav = this.shadowRoot.querySelector('.nav');

        burgerMenu.addEventListener('click', () => {
            nav.classList.toggle('active');
        });

        // Добавляем обработчики для модального окна
        const modal = this.shadowRoot.querySelector('.modal');
        const modalClose = this.shadowRoot.querySelector('.modal-close');
        const pricingTrigger = this.shadowRoot.querySelector('.pricing-trigger');

        pricingTrigger.addEventListener('click', () => {
            modal.classList.add('active');
        });

        modalClose.addEventListener('click', () => {
            modal.classList.remove('active');
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });

        // Добавляем обработчики для кнопок в модальном окне
        const modalButtons = this.shadowRoot.querySelectorAll('.modal .button');
        modalButtons.forEach(button => {
            button.addEventListener('click', () => {
                const plan = button.closest('.pricing-card').querySelector('.card-title').textContent;
                this.dispatchEvent(new CustomEvent('plan-selected', {
                    detail: { plan }
                }));
                modal.classList.remove('active');
            });
        });

        // Добавляем обработчики для авторизации
        const authTrigger = this.shadowRoot.querySelector('.auth-trigger');
        const authComponent = this.shadowRoot.querySelector('auth-component');

        authTrigger.addEventListener('click', () => {
            authComponent.open();
        });

        authComponent.addEventListener('auth-success', () => {
            // Обновляем UI после успешной авторизации
            authTrigger.textContent = 'Профиль';
            authTrigger.classList.add('active');
        });
    }
}

customElements.define('header-component', HeaderComponent); 