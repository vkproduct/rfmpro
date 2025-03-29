class UploadComponent extends HTMLElement {
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
                .upload-area {
                    border: 2px dashed var(--border);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-xl);
                    text-align: center;
                    background: var(--background-alt);
                    transition: all 0.2s ease;
                    cursor: pointer;
                }
                .upload-area:hover {
                    border-color: var(--primary);
                    background: var(--background);
                    transform: translateY(-1px);
                }
                .upload-area.dragover {
                    border-color: var(--primary);
                    background: var(--background);
                    transform: translateY(-1px);
                }
                .file-input {
                    display: none;
                }
                .upload-icon {
                    font-size: 3rem;
                    margin-bottom: var(--spacing-md);
                    color: var(--primary);
                }
                .upload-text {
                    font-size: 1.5rem;
                    color: var(--text);
                    margin-bottom: var(--spacing-sm);
                    font-weight: 500;
                }
                .upload-subtext {
                    color: var(--text-light);
                    font-size: 1.125rem;
                }
                .column-select {
                    display: none;
                    margin-top: var(--spacing-xl);
                    background: var(--background);
                    padding: var(--spacing-lg);
                    border-radius: var(--radius-lg);
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    border: 1px solid var(--border);
                }
                .column-select.active {
                    display: block;
                    animation: fadeIn 0.3s ease-out;
                }
                .column-select h3 {
                    font-size: 1.75rem;
                    font-weight: 600;
                    margin-bottom: var(--spacing-lg);
                    color: var(--text);
                    letter-spacing: -0.02em;
                }
                select {
                    width: 100%;
                    padding: var(--spacing-md);
                    margin: var(--spacing-sm) 0;
                    border: 2px solid var(--border);
                    border-radius: var(--radius);
                    background: var(--background);
                    color: var(--text);
                    font-size: 1.125rem;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-family: var(--font-sans);
                }
                select:hover {
                    border-color: var(--primary);
                }
                select:focus {
                    outline: none;
                    border-color: var(--primary);
                    box-shadow: 0 0 0 3px rgba(255, 90, 95, 0.1);
                }
                .button {
                    width: 100%;
                    padding: var(--spacing-md);
                    margin-top: var(--spacing-lg);
                    font-size: 1.125rem;
                }
                .error {
                    color: var(--primary);
                    margin-top: var(--spacing-md);
                    padding: var(--spacing-md);
                    background: #FFF1F3;
                    border-radius: var(--radius);
                    display: none;
                    font-size: 1.125rem;
                }
                .error.visible {
                    display: block;
                    animation: fadeIn 0.3s ease-out;
                }
                .success {
                    color: #34C759;
                    margin-top: var(--spacing-md);
                    padding: var(--spacing-md);
                    background: #F0FFF4;
                    border-radius: var(--radius);
                    display: none;
                    font-size: 1.125rem;
                }
                .success.visible {
                    display: block;
                    animation: fadeIn 0.3s ease-out;
                }
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            </style>
            <div class="section-header">
                <h2>Загрузите данные</h2>
                <p>Выберите CSV или Excel файл с данными о покупках ваших клиентов</p>
            </div>
            <div class="upload-area">
                <input type="file" class="file-input" accept=".csv,.xlsx,.xls">
                <div class="upload-icon">📁</div>
                <div class="upload-text">Перетащите файл сюда или кликните для выбора</div>
                <div class="upload-subtext">Поддерживаемые форматы: CSV, Excel</div>
            </div>
            <div class="column-select">
                <h3>Выберите столбцы</h3>
                <select class="client-id-select">
                    <option value="">ID клиента</option>
                </select>
                <select class="date-select">
                    <option value="">Дата покупки</option>
                </select>
                <select class="amount-select">
                    <option value="">Сумма покупки</option>
                </select>
                <button class="button primary">Загрузить</button>
            </div>
            <div class="error"></div>
            <div class="success"></div>
        `;

        const uploadArea = this.shadowRoot.querySelector('.upload-area');
        const fileInput = this.shadowRoot.querySelector('.file-input');
        const columnSelect = this.shadowRoot.querySelector('.column-select');
        const uploadBtn = this.shadowRoot.querySelector('.button');
        const errorDiv = this.shadowRoot.querySelector('.error');
        const successDiv = this.shadowRoot.querySelector('.success');

        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            uploadArea.classList.add('dragover');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('dragover');
        }

        uploadArea.addEventListener('drop', handleDrop, false);
        uploadArea.addEventListener('click', () => fileInput.click());

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'text/csv' || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            let data;
                            if (file.type === 'text/csv') {
                                data = parseCSV(e.target.result);
                            } else {
                                // Для Excel файлов нужно использовать библиотеку SheetJS
                                // Здесь просто заглушка
                                data = [];
                            }
                            if (data.length > 0) {
                                populateColumnSelects(data[0]);
                                columnSelect.classList.add('active');
                                showSuccess('Файл успешно загружен');
                            }
                        } catch (error) {
                            showError('Ошибка при чтении файла');
                        }
                    };
                    reader.readAsText(file);
                } else {
                    showError('Неподдерживаемый формат файла');
                }
            }
        }

        function parseCSV(text) {
            const lines = text.split('\n');
            return lines.map(line => {
                // Обработка кавычек и запятых внутри кавычек
                const cells = [];
                let currentCell = '';
                let insideQuotes = false;
                
                for (let i = 0; i < line.length; i++) {
                    const char = line[i];
                    if (char === '"') {
                        insideQuotes = !insideQuotes;
                    } else if (char === ',' && !insideQuotes) {
                        cells.push(currentCell.trim());
                        currentCell = '';
                    } else {
                        currentCell += char;
                    }
                }
                cells.push(currentCell.trim());
                
                return cells;
            }).filter(line => line.length > 0 && line.some(cell => cell.trim() !== ''));
        }

        function populateColumnSelects(headers) {
            const selects = this.shadowRoot.querySelectorAll('select');
            selects.forEach(select => {
                select.innerHTML = '<option value="">Выберите столбец</option>';
                headers.forEach(header => {
                    const option = document.createElement('option');
                    option.value = header;
                    option.textContent = header;
                    select.appendChild(option);
                });
            });
        }

        function showError(message) {
            errorDiv.textContent = message;
            errorDiv.classList.add('visible');
            successDiv.classList.remove('visible');
        }

        function showSuccess(message) {
            successDiv.textContent = message;
            successDiv.classList.add('visible');
            errorDiv.classList.remove('visible');
        }

        uploadBtn.addEventListener('click', async () => {
            const clientIdCol = this.shadowRoot.querySelector('.client-id-select').value;
            const dateCol = this.shadowRoot.querySelector('.date-select').value;
            const amountCol = this.shadowRoot.querySelector('.amount-select').value;

            if (!clientIdCol || !dateCol || !amountCol) {
                showError('Пожалуйста, выберите все необходимые столбцы');
                return;
            }

            await this.uploadData();
        });
    }

    async uploadData() {
        const token = localStorage.getItem('token');
        if (!token) {
            showError('Пожалуйста, войдите в систему');
            return;
        }

        const fileInput = this.shadowRoot.querySelector('.file-input');
        const file = fileInput.files[0];
        if (!file) {
            showError('Пожалуйста, выберите файл');
            return;
        }

        // Проверка формата файла
        const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!validTypes.includes(file.type)) {
            showError('Поддерживаются только файлы CSV и Excel');
            return;
        }

        const clientIdCol = this.shadowRoot.querySelector('.client-id-select').value;
        const dateCol = this.shadowRoot.querySelector('.date-select').value;
        const amountCol = this.shadowRoot.querySelector('.amount-select').value;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('client_id_col', clientIdCol);
        formData.append('date_col', dateCol);
        formData.append('amount_col', amountCol);

        try {
            const uploadBtn = this.shadowRoot.querySelector('.button');
            uploadBtn.disabled = true;
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка загрузки данных');
            }

            const result = await response.json();
            showSuccess('Файл успешно загружен');
            this.dispatchEvent(new CustomEvent('upload-success'));
        } catch (error) {
            console.error('Ошибка:', error);
            showError(error.message || 'Ошибка при загрузке файла');
        } finally {
            uploadBtn.disabled = false;
        }
    }
}

customElements.define('upload-component', UploadComponent); 