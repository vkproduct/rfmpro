class HeroComponent extends HTMLElement {
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
                .hero {
                    background: var(--background-alt);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-xl);
                    margin-bottom: var(--spacing-xl);
                    position: relative;
                    overflow: hidden;
                }
                .hero::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
                    opacity: 0.05;
                    z-index: 1;
                }
                .hero-content {
                    position: relative;
                    z-index: 2;
                    max-width: 800px;
                    margin: 0 auto;
                    text-align: center;
                }
                .hero-title {
                    font-size: 3.5rem;
                    font-weight: 700;
                    color: var(--text);
                    margin-bottom: var(--spacing-lg);
                    line-height: 1.1;
                    letter-spacing: -0.03em;
                }
                .hero-subtitle {
                    font-size: 1.5rem;
                    color: var(--text-light);
                    margin-bottom: var(--spacing-xl);
                    line-height: 1.4;
                }
                .hero-buttons {
                    display: flex;
                    gap: var(--spacing-md);
                    justify-content: center;
                    margin-bottom: var(--spacing-xl);
                }
                .button {
                    padding: var(--spacing-md) var(--spacing-xl);
                    border-radius: var(--radius);
                    font-size: 1.125rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
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
                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: var(--spacing-lg);
                    margin-top: var(--spacing-xl);
                }
                .feature-card {
                    background: var(--background);
                    padding: var(--spacing-lg);
                    border-radius: var(--radius-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .feature-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                }
                .feature-icon {
                    font-size: 2.5rem;
                    margin-bottom: var(--spacing-md);
                    color: var(--primary);
                }
                .feature-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--text);
                    margin-bottom: var(--spacing-sm);
                }
                .feature-description {
                    color: var(--text-light);
                    line-height: 1.6;
                    font-size: 1.125rem;
                }
                @media (max-width: 768px) {
                    .hero-title {
                        font-size: 2.5rem;
                    }
                    .hero-subtitle {
                        font-size: 1.25rem;
                    }
                    .hero-buttons {
                        flex-direction: column;
                    }
                    .button {
                        width: 100%;
                    }
                }
            </style>
            <div class="hero">
                <div class="hero-content">
                    <h1 class="hero-title">RFM Pro</h1>
                    <p class="hero-subtitle">Профессиональный инструмент для анализа клиентской базы и сегментации</p>
                    <div class="hero-buttons">
                        <button class="button primary">Начать анализ</button>
                        <button class="button secondary">Узнать больше</button>
                    </div>
                </div>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3 class="feature-title">Быстрый анализ</h3>
                    <p class="feature-description">Получите результаты анализа вашей клиентской базы за считанные минуты</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3 class="feature-title">Точные данные</h3>
                    <p class="feature-description">Точные метрики и сегментация на основе реальных данных</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Наглядные результаты</h3>
                    <p class="feature-description">Понятные графики и отчеты для принятия решений</p>
                </div>
            </div>
        `;

        // Добавляем обработчики для кнопок
        const startButton = this.shadowRoot.querySelector('.button.primary');
        const learnMoreButton = this.shadowRoot.querySelector('.button.secondary');

        startButton.addEventListener('click', () => {
            this.dispatchEvent(new CustomEvent('start-analysis'));
        });

        learnMoreButton.addEventListener('click', () => {
            this.dispatchEvent(new CustomEvent('learn-more'));
        });
    }
}

customElements.define('hero-component', HeroComponent); 