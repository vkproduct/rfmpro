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
                    max-width: 800px;
                    margin: 2rem auto;
                    padding: 2rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .upload-area {
                    border: 2px dashed #ddd;
                    border-radius: 8px;
                    padding: 2rem;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                .upload-area:hover {
                    border-color: #FF5A5F;
                }
                .upload-area.dragover {
                    border-color: #FF5A5F;
                    background: rgba(255,90,95,0.1);
                }
                .file-input {
                    display: none;
                }
                .column-select {
                    display: none;
                    margin-top: 2rem;
                }
                .column-select.active {
                    display: block;
                }
                select {
                    width: 100%;
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                button {
                    background: #FF5A5F;
                    color: white;
                    border: none;
                    padding: 0.8rem 1.5rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: background 0.3s;
                }
                button:hover {
                    background: #ff4449;
                }
                button:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }
                .error {
                    color: #ff4449;
                    margin-top: 1rem;
                }
            </style>
            <div class="upload-area">
                <input type="file" class="file-input" accept=".csv,.xlsx,.xls">
                <p>Перетащите файл сюда или кликните для выбора</p>
                <p>Поддерживаемые форматы: CSV, Excel</p>
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
                <button class="upload-btn">Загрузить</button>
            </div>
            <div class="error"></div>
        `;

        const uploadArea = this.shadowRoot.querySelector('.upload-area');
        const fileInput = this.shadowRoot.querySelector('.file-input');
        const columnSelect = this.shadowRoot.querySelector('.column-select');
        const uploadBtn = this.shadowRoot.querySelector('.upload-btn');
        const errorDiv = this.shadowRoot.querySelector('.error');

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
            const lines = text.split('\\n');
            return lines.map(line => line.split(',').map(cell => cell.trim()));
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
        }

        uploadBtn.addEventListener('click', async () => {
            const clientIdCol = this.shadowRoot.querySelector('.client-id-select').value;
            const dateCol = this.shadowRoot.querySelector('.date-select').value;
            const amountCol = this.shadowRoot.querySelector('.amount-select').value;

            if (!clientIdCol || !dateCol || !amountCol) {
                showError('Пожалуйста, выберите все необходимые столбцы');
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('client_id_col', clientIdCol);
            formData.append('date_col', dateCol);
            formData.append('amount_col', amountCol);

            try {
                uploadBtn.disabled = true;
                const response = await fetch('http://localhost:8000/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Ошибка загрузки');
                }

                const result = await response.json();
                showError('Файл успешно загружен');
                this.dispatchEvent(new CustomEvent('upload-success'));
            } catch (error) {
                showError('Ошибка при загрузке файла');
            } finally {
                uploadBtn.disabled = false;
            }
        });
    }
}

customElements.define('upload-component', UploadComponent); 