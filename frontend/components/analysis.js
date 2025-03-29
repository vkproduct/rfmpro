class AnalysisComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    max-width: 1200px;
                    margin: 2rem auto;
                    padding: 2rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .analysis-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
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
                .results-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 1rem;
                    margin-top: 2rem;
                }
                .result-card {
                    padding: 1.5rem;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background: #f9f9f9;
                }
                .result-card h3 {
                    margin: 0 0 1rem 0;
                    color: #333;
                }
                .metric {
                    display: flex;
                    justify-content: space-between;
                    margin: 0.5rem 0;
                    padding: 0.5rem;
                    background: white;
                    border-radius: 4px;
                }
                .metric-name {
                    color: #666;
                }
                .metric-value {
                    font-weight: 500;
                }
                .error {
                    color: #ff4449;
                    margin-top: 1rem;
                }
                .loading {
                    text-align: center;
                    padding: 2rem;
                    color: #666;
                }
            </style>
            <div class="analysis-header">
                <h2>RFM Анализ</h2>
                <button class="analyze-btn">Запустить анализ</button>
            </div>
            <div class="results-grid"></div>
            <div class="error"></div>
        `;

        const analyzeBtn = this.shadowRoot.querySelector('.analyze-btn');
        const resultsGrid = this.shadowRoot.querySelector('.results-grid');
        const errorDiv = this.shadowRoot.querySelector('.error');

        analyzeBtn.addEventListener('click', async () => {
            try {
                analyzeBtn.disabled = true;
                resultsGrid.innerHTML = '<div class="loading">Загрузка результатов...</div>';
                errorDiv.textContent = '';

                const response = await fetch('http://localhost:8000/analyze');
                if (!response.ok) {
                    throw new Error('Ошибка получения результатов');
                }

                const results = await response.json();
                displayResults(results);
            } catch (error) {
                errorDiv.textContent = 'Ошибка при получении результатов анализа';
                resultsGrid.innerHTML = '';
            } finally {
                analyzeBtn.disabled = false;
            }
        });

        function displayResults(results) {
            resultsGrid.innerHTML = '';
            results.forEach(result => {
                const card = document.createElement('div');
                card.className = 'result-card';
                card.innerHTML = `
                    <h3>Клиент ${result.client_id}</h3>
                    <div class="metric">
                        <span class="metric-name">Recency (дни)</span>
                        <span class="metric-value">${result.Recency}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-name">Frequency</span>
                        <span class="metric-value">${result.Frequency}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-name">Monetary</span>
                        <span class="metric-value">${result.Monetary.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-name">RFM Score</span>
                        <span class="metric-value">${result.RFM_Score}</span>
                    </div>
                `;
                resultsGrid.appendChild(card);
            });
        }
    }
}

customElements.define('analysis-component', AnalysisComponent); 