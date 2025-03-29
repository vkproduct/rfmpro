class FooterComponent extends HTMLElement {
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
                footer {
                    background: var(--background-alt);
                    border-top: 1px solid var(--border);
                    padding: var(--spacing-xl) 0;
                    margin-top: var(--spacing-xl);
                }
                .footer-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 var(--spacing-md);
                }
                .footer-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--spacing-xl);
                    margin-bottom: var(--spacing-xl);
                }
                .footer-section h3 {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--text);
                    margin-bottom: var(--spacing-md);
                }
                .footer-section p {
                    color: var(--text-light);
                    line-height: 1.6;
                    margin-bottom: var(--spacing-md);
                }
                .footer-links {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                .footer-links li {
                    margin-bottom: var(--spacing-sm);
                }
                .footer-links a {
                    color: var(--text-light);
                    text-decoration: none;
                    transition: color 0.2s;
                }
                .footer-links a:hover {
                    color: var(--primary);
                }
                .social-links {
                    display: flex;
                    gap: var(--spacing-md);
                    margin-top: var(--spacing-md);
                }
                .social-link {
                    color: var(--text-light);
                    font-size: 1.5rem;
                    transition: color 0.2s;
                }
                .social-link:hover {
                    color: var(--primary);
                }
                .footer-bottom {
                    border-top: 1px solid var(--border);
                    padding-top: var(--spacing-lg);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: var(--spacing-md);
                }
                .copyright {
                    color: var(--text-light);
                    font-size: 0.875rem;
                }
                .footer-bottom-links {
                    display: flex;
                    gap: var(--spacing-lg);
                }
                .footer-bottom-links a {
                    color: var(--text-light);
                    text-decoration: none;
                    font-size: 0.875rem;
                    transition: color 0.2s;
                }
                .footer-bottom-links a:hover {
                    color: var(--primary);
                }
                @media (max-width: 768px) {
                    .footer-grid {
                        grid-template-columns: 1fr;
                        gap: var(--spacing-lg);
                    }
                    .footer-bottom {
                        flex-direction: column;
                        text-align: center;
                    }
                    .footer-bottom-links {
                        justify-content: center;
                    }
                }
            </style>
            <footer>
                <div class="footer-content">
                    <div class="footer-grid">
                        <div class="footer-section">
                            <h3>RFM Pro</h3>
                            <p>Профессиональный инструмент для анализа клиентской базы и сегментации</p>
                            <div class="social-links">
                                <a href="#" class="social-link">🐦</a>
                                <a href="#" class="social-link">💼</a>
                                <a href="#" class="social-link">📚</a>
                            </div>
                        </div>
                        <div class="footer-section">
                            <h3>Продукт</h3>
                            <ul class="footer-links">
                                <li><a href="#features">Возможности</a></li>
                                <li><a href="#pricing">Тарифы</a></li>
                                <li><a href="#how-it-works">Как это работает</a></li>
                                <li><a href="#api">API</a></li>
                            </ul>
                        </div>
                        <div class="footer-section">
                            <h3>Компания</h3>
                            <ul class="footer-links">
                                <li><a href="#about">О нас</a></li>
                                <li><a href="#blog">Блог</a></li>
                                <li><a href="#careers">Карьера</a></li>
                                <li><a href="#press">Пресса</a></li>
                            </ul>
                        </div>
                        <div class="footer-section">
                            <h3>Поддержка</h3>
                            <ul class="footer-links">
                                <li><a href="#help">Центр помощи</a></li>
                                <li><a href="#docs">Документация</a></li>
                                <li><a href="#contact">Контакты</a></li>
                                <li><a href="#status">Статус</a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="footer-bottom">
                        <div class="copyright">
                            © 2024 RFM Pro. Все права защищены.
                        </div>
                        <div class="footer-bottom-links">
                            <a href="#privacy">Конфиденциальность</a>
                            <a href="#terms">Условия использования</a>
                            <a href="#cookies">Cookies</a>
                        </div>
                    </div>
                </div>
            </footer>
        `;
    }
}

customElements.define('footer-component', FooterComponent); 