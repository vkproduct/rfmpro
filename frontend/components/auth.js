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
                    margin-bottom: var(--spacing-lg);
                    letter-spacing: -0.02em;
                }
                .form-group {
                    margin-bottom: var(--spacing-md);
                }
                .form-label {
                    display: block;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: var(--text);
                    margin-bottom: var(--spacing-xs);
                }
                .form-input {
                    width: 100%;
                    padding: var(--spacing-sm);
                    border: 1px solid var(--border);
                    border-radius: var(--radius);
                    font-size: 1rem;
                    transition: all 0.2s ease;
                }
                .form-input:focus {
                    outline: none;
                    border-color: var(--primary);
                    box-shadow: 0 0 0 2px rgba(255, 90, 95, 0.1);
                }
                .button {
                    width: 100%;
                    padding: var(--spacing-sm);
                    border-radius: var(--radius);
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-size: 1rem;
                    margin-bottom: var(--spacing-sm);
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
                .error-message {
                    color: var(--primary);
                    font-size: 0.875rem;
                    margin-top: var(--spacing-xs);
                    display: none;
                }
                .error-message.visible {
                    display: block;
                }
                .success-message {
                    color: #4CAF50;
                    font-size: 0.875rem;
                    margin-top: var(--spacing-xs);
                    display: none;
                }
                .success-message.visible {
                    display: block;
                }
            </style>
            <div class="modal">
                <div class="modal-content">
                    <div class="modal-close">×</div>
                    <h2 class="modal-title">Вход</h2>
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-input" id="email" placeholder="your@email.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Пароль</label>
                        <input type="password" class="form-input" id="password" placeholder="••••••••">
                    </div>
                    <div class="error-message" id="error-message"></div>
                    <div class="success-message" id="success-message"></div>
                    <button class="button primary" id="login-btn">Войти</button>
                    <button class="button secondary" id="signup-btn">Регистрация</button>
                </div>
            </div>
        `;

        // Добавляем обработчики для модального окна
        const modal = this.shadowRoot.querySelector('.modal');
        const modalClose = this.shadowRoot.querySelector('.modal-close');
        const loginBtn = this.shadowRoot.querySelector('#login-btn');
        const signupBtn = this.shadowRoot.querySelector('#signup-btn');
        const errorMessage = this.shadowRoot.querySelector('#error-message');
        const successMessage = this.shadowRoot.querySelector('#success-message');

        // Функция для показа сообщений
        const showMessage = (message, isError = false) => {
            errorMessage.textContent = isError ? message : '';
            errorMessage.classList.toggle('visible', isError);
            successMessage.textContent = isError ? '' : message;
            successMessage.classList.toggle('visible', !isError);
        };

        // Функция для очистки сообщений
        const clearMessages = () => {
            errorMessage.classList.remove('visible');
            successMessage.classList.remove('visible');
        };

        // Обработчик для входа
        loginBtn.addEventListener('click', async () => {
            clearMessages();
            const email = this.shadowRoot.querySelector('#email').value;
            const password = this.shadowRoot.querySelector('#password').value;

            try {
                const { data, error } = await window.supabase.auth.signInWithPassword({
                    email,
                    password
                });

                if (error) throw error;

                localStorage.setItem('token', data.session.access_token);
                showMessage('Успешный вход!');
                setTimeout(() => {
                    modal.classList.remove('active');
                    this.dispatchEvent(new CustomEvent('auth-success'));
                }, 1000);
            } catch (error) {
                showMessage(error.message, true);
            }
        });

        // Обработчик для регистрации
        signupBtn.addEventListener('click', async () => {
            clearMessages();
            const email = this.shadowRoot.querySelector('#email').value;
            const password = this.shadowRoot.querySelector('#password').value;

            try {
                const { data, error } = await window.supabase.auth.signUp({
                    email,
                    password
                });

                if (error) throw error;

                showMessage('Регистрация успешна! Проверьте email для подтверждения.');
            } catch (error) {
                showMessage(error.message, true);
            }
        });

        // Обработчики для закрытия модального окна
        modalClose.addEventListener('click', () => {
            modal.classList.remove('active');
            clearMessages();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                clearMessages();
            }
        });

        // Метод для открытия модального окна
        this.open = () => {
            modal.classList.add('active');
            clearMessages();
        };
    }
}

customElements.define('auth-component', AuthComponent); 