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
                    background: #fff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .header {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 1rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .logo {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #FF5A5F;
                    text-decoration: none;
                }
                .nav-menu {
                    display: flex;
                    gap: 2rem;
                }
                .nav-menu a {
                    color: #333;
                    text-decoration: none;
                    font-weight: 500;
                }
                .burger {
                    display: none;
                    cursor: pointer;
                }
                .burger span {
                    display: block;
                    width: 25px;
                    height: 3px;
                    background: #333;
                    margin: 5px 0;
                    transition: 0.3s;
                }
                .pricing-modal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 1000;
                }
                .modal-content {
                    background: white;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 2rem;
                    border-radius: 8px;
                }
                .close {
                    float: right;
                    cursor: pointer;
                    font-size: 1.5rem;
                }
                .pricing-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 1rem;
                    margin-top: 2rem;
                }
                .pricing-card {
                    padding: 1.5rem;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    text-align: center;
                }
                .price {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #FF5A5F;
                }
                @media (max-width: 768px) {
                    .nav-menu {
                        display: none;
                        position: absolute;
                        top: 100%;
                        left: 0;
                        right: 0;
                        background: white;
                        padding: 1rem;
                        flex-direction: column;
                        text-align: center;
                    }
                    .nav-menu.active {
                        display: flex;
                    }
                    .burger {
                        display: block;
                    }
                }
            </style>
            <header class="header">
                <a href="#" class="logo">RFM Pro</a>
                <div class="burger">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <nav class="nav-menu">
                    <a href="#" class="pricing-trigger">Тарифы</a>
                    <a href="#">Документация</a>
                    <a href="#">Поддержка</a>
                </nav>
            </header>
            <div class="pricing-modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h2>Тарифы</h2>
                    <div class="pricing-grid">
                        <div class="pricing-card">
                            <h3>Базовый</h3>
                            <div class="price">0 ₽</div>
                            <ul>
                                <li>До 1000 записей</li>
                                <li>Базовый RFM анализ</li>
                                <li>CSV/Excel импорт</li>
                            </ul>
                        </div>
                        <div class="pricing-card">
                            <h3>Про</h3>
                            <div class="price">590 ₽</div>
                            <ul>
                                <li>До 10000 записей</li>
                                <li>Расширенный анализ</li>
                                <li>API доступ</li>
                            </ul>
                        </div>
                        <div class="pricing-card">
                            <h3>Бизнес</h3>
                            <div class="price">1990 ₽</div>
                            <ul>
                                <li>Безлимитные записи</li>
                                <li>Все функции</li>
                                <li>Приоритетная поддержка</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Бургер меню
        const burger = this.shadowRoot.querySelector('.burger');
        const navMenu = this.shadowRoot.querySelector('.nav-menu');
        burger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });

        // Модальное окно тарифов
        const pricingTrigger = this.shadowRoot.querySelector('.pricing-trigger');
        const modal = this.shadowRoot.querySelector('.pricing-modal');
        const closeBtn = this.shadowRoot.querySelector('.close');

        pricingTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            modal.style.display = 'block';
        });

        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
}

customElements.define('header-component', HeaderComponent); 