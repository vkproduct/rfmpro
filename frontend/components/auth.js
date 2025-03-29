class AuthComponent extends HTMLElement {
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
                    max-width: 400px;
                    width: 90%;
                    position: relative;
                    box-shadow: var(--shadow-lg);
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
                .form-group {
                    margin-bottom: var(--spacing-md);
                }
                .form-group label {
                    display: block;
                    margin-bottom: var(--spacing-xs);
                    color: var(--text);
                    font-weight: 500;
                }
                .form-group input {
                    width: 100%;
                    padding: var(--spacing-sm);
                    border: 1px solid var(--border);
                    border-radius: var(--radius);
                    font-size: 1rem;
                    transition: border-color 0.2s ease;
                }
                .form-group input:focus {
                    outline: none;
                    border-color: var(--primary);
                }
                .button {
                    width: 100%;
                    padding: var(--spacing-sm);
                    border-radius: var(--radius);
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-size: 1rem;
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
                .tabs {
                    display: flex;
                    margin-bottom: var(--spacing-md);
                    border-bottom: 1px solid var(--border);
                }
                .tab {
                    padding: var(--spacing-sm) var(--spacing-md);
                    cursor: pointer;
                    color: var(--text-light);
                    font-weight: 500;
                    transition: all 0.2s ease;
                }
                .tab.active {
                    color: var(--primary);
                    border-bottom: 2px solid var(--primary);
                }
                .error {
                    color: var(--error);
                    font-size: 0.875rem;
                    margin-top: var(--spacing-xs);
                }
                .success {
                    color: var(--success);
                    font-size: 0.875rem;
                    margin-top: var(--spacing-xs);
                }
            </style>
            <div class="modal">
                <div class="modal-content">
                    <div class="modal-close">×</div>
                    <div class="tabs">
                        <div class="tab active" data-tab="login">Вход</div>
                        <div class="tab" data-tab="register">Регистрация</div>
                    </div>
                    <div id="login-form">
                        <h2 class="modal-title">Вход</h2>
                        <form>
                            <div class="form-group">
                                <label for="login-email">Email</label>
                                <input type="email" id="login-email" required>
                            </div>
                            <div class="form-group">
                                <label for="login-password">Пароль</label>
                                <input type="password" id="login-password" required>
                            </div>
                            <div class="error" id="login-error"></div>
                            <button type="submit" class="button primary">Войти</button>
                        </form>
                    </div>
                    <div id="register-form" style="display: none;">
                        <h2 class="modal-title">Регистрация</h2>
                        <form>
                            <div class="form-group">
                                <label for="register-email">Email</label>
                                <input type="email" id="register-email" required>
                            </div>
                            <div class="form-group">
                                <label for="register-password">Пароль</label>
                                <input type="password" id="register-password" required>
                            </div>
                            <div class="error" id="register-error"></div>
                            <button type="submit" class="button primary">Зарегистрироваться</button>
                        </form>
                    </div>
                </div>
            </div>
        `;

        // Добавляем обработчики для модального окна
        const modal = this.shadowRoot.querySelector('.modal');
        const modalClose = this.shadowRoot.querySelector('.modal-close');

        modalClose.addEventListener('click', () => {
            this.close();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.close();
            }
        });

        // Добавляем обработчики для табов
        const tabs = this.shadowRoot.querySelectorAll('.tab');
        const loginForm = this.shadowRoot.querySelector('#login-form');
        const registerForm = this.shadowRoot.querySelector('#register-form');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                if (tab.dataset.tab === 'login') {
                    loginForm.style.display = 'block';
                    registerForm.style.display = 'none';
                } else {
                    loginForm.style.display = 'none';
                    registerForm.style.display = 'block';
                }
            });
        });

        // Добавляем обработчики для форм
        const loginFormElement = loginForm.querySelector('form');
        const registerFormElement = registerForm.querySelector('form');

        loginFormElement.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = loginFormElement.querySelector('#login-email').value;
            const password = loginFormElement.querySelector('#login-password').value;
            const errorElement = loginFormElement.querySelector('.error');

            try {
                const { data, error } = await window.supabase.auth.signInWithPassword({
                    email,
                    password
                });

                if (error) throw error;

                localStorage.setItem('token', data.session.access_token);
                document.dispatchEvent(new CustomEvent('auth-success'));
                this.close();
            } catch (error) {
                errorElement.textContent = error.message;
            }
        });

        registerFormElement.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = registerFormElement.querySelector('#register-email').value;
            const password = registerFormElement.querySelector('#register-password').value;
            const errorElement = registerFormElement.querySelector('.error');

            try {
                const { data, error } = await window.supabase.auth.signUp({
                    email,
                    password
                });

                if (error) throw error;

                errorElement.textContent = 'Проверьте email для подтверждения регистрации';
                errorElement.classList.add('success');
            } catch (error) {
                errorElement.textContent = error.message;
                errorElement.classList.remove('success');
            }
        });
    }

    open() {
        this.shadowRoot.querySelector('.modal').classList.add('active');
    }

    close() {
        this.shadowRoot.querySelector('.modal').classList.remove('active');
        this.shadowRoot.querySelectorAll('.error').forEach(el => el.textContent = '');
    }
}

customElements.define('auth-component', AuthComponent); 