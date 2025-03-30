/**
 * Утилиты для работы с графиками на основе ApexCharts
 */
const ChartUtils = (function() {
    /**
     * Создает столбчатую диаграмму на основе данных сегментов
     * @param {string} containerId ID контейнера для графика
     * @param {Array} data Массив данных {name, value}
     * @param {string} title Заголовок графика
     * @returns {Object} Экземпляр графика
     */
    function createBarChart(containerId, data, title) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return null;
        }
        
        const options = {
            series: [{
                name: 'Количество',
                data: data.map(item => item.value)
            }],
            chart: {
                type: 'bar',
                height: 300,
                toolbar: {
                    show: false
                }
            },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    dataLabels: {
                        position: 'top'
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return val;
                },
                offsetY: -20,
                style: {
                    fontSize: '12px',
                    colors: ["#304758"]
                }
            },
            xaxis: {
                categories: data.map(item => item.name),
                position: 'bottom',
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                tooltip: {
                    enabled: true
                }
            },
            yaxis: {
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: true,
                    formatter: function(val) {
                        return val;
                    }
                }
            },
            title: {
                text: title || 'Распределение по сегментам',
                floating: false,
                offsetY: 0,
                align: 'center',
                style: {
                    color: '#444'
                }
            },
            colors: ['#4f46e5']
        };
        
        try {
            container.innerHTML = '';
            const chart = new ApexCharts(container, options);
            chart.render();
            return chart;
        } catch (error) {
            console.error('Ошибка при создании столбчатой диаграммы:', error);
            return null;
        }
    }
    
    /**
     * Создает линейную диаграмму для отображения RFM-оценок
     * @param {string} containerId ID контейнера для графика
     * @param {Array} data Массив данных {name, value}
     * @param {string} title Заголовок графика
     * @returns {Object} Экземпляр графика
     */
    function createLineChart(containerId, data, title) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return null;
        }
        
        // Сортируем данные по значению name
        const sortedData = [...data].sort((a, b) => parseInt(a.name) - parseInt(b.name));
        
        const options = {
            series: [{
                name: 'Количество',
                data: sortedData.map(item => item.value)
            }],
            chart: {
                type: 'line',
                height: 300,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                }
            },
            dataLabels: {
                enabled: true
            },
            stroke: {
                curve: 'straight',
                width: 3
            },
            markers: {
                size: 5
            },
            xaxis: {
                categories: sortedData.map(item => item.name),
                title: {
                    text: 'RFM-Score'
                }
            },
            yaxis: {
                title: {
                    text: 'Количество клиентов'
                }
            },
            grid: {
                borderColor: '#e7e7e7',
                row: {
                    colors: ['#f3f3f3', 'transparent'],
                    opacity: 0.5
                }
            },
            title: {
                text: title || 'Распределение по RFM-оценке',
                align: 'center',
                style: {
                    color: '#444'
                }
            },
            colors: ['#3b82f6']
        };
        
        try {
            container.innerHTML = '';
            const chart = new ApexCharts(container, options);
            chart.render();
            return chart;
        } catch (error) {
            console.error('Ошибка при создании линейной диаграммы:', error);
            return null;
        }
    }
    
    /**
     * Создает круговую диаграмму для отображения сегментов
     * @param {string} containerId ID контейнера для графика
     * @param {Array} data Массив данных {name, value}
     * @param {string} title Заголовок графика
     * @returns {Object} Экземпляр графика
     */
    /**
 * Создает кольцевую диаграмму для отображения сегментов
 * @param {string} containerId ID контейнера для графика
 * @param {Array} data Массив данных {name, value}
 * @param {string} title Заголовок графика
 * @returns {Object} Экземпляр графика
 */
    function createPieChart(containerId, data, title) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return null;
        }
        
        const options = {
            series: data.map(item => item.value),
            chart: {
                type: 'donut',  // Изменили тип на donut
                height: 300,
                toolbar: {
                    show: false
                }
            },
            labels: data.map(item => item.name),
            responsive: [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 200
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }],
            legend: {
                position: 'bottom'
            },
            plotOptions: {
                pie: {
                    donut: {
                        size: '60%',  // Увеличиваем размер отверстия
                        labels: {
                            show: true,
                            name: {
                                show: true
                            },
                            value: {
                                show: true,
                                formatter: function(val) {
                                    return val;
                                }
                            },
                            total: {
                                show: true,
                                label: 'Всего',
                                formatter: function(w) {
                                    return w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                }
                            }
                        }
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: function(val, opts) {
                    return Math.round(val) + '%';
                }
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val;
                    }
                }
            },
            title: {
                text: title || 'Распределение клиентов по сегментам',
                align: 'center',
                style: {
                    color: '#444'
                }
            },
            colors: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280', '#059669', '#9333ea']
        };
        
        try {
            container.innerHTML = '';
            const chart = new ApexCharts(container, options);
            chart.render();
            return chart;
        } catch (error) {
            console.error('Ошибка при создании кольцевой диаграммы:', error);
            return null;
        }
    }
    
    /**
     * Инициализирует все графики на странице
     * @param {string} activeTab Активная вкладка
     */
    function initializeCharts(activeTab) {
        const state = DataService.getState();
        
        if (!state.rfmData || !state.rfmData.segments) {
            console.warn('Нет данных для графиков');
            return;
        }
        
        // Формируем данные для графиков
        const segmentData = Object.entries(state.rfmData.segments).map(([name, count]) => ({
            name,
            value: count
        }));
        
        // Графики для вкладки "Обзор"
        if (activeTab === 'overview') {
            if (document.getElementById('segments-chart')) {
                createBarChart('segments-chart', segmentData);
            }
            
            if (document.getElementById('rfm-scores-chart') && state.rfmData.rfm_scores) {
                const rfmScoreData = Object.entries(state.rfmData.rfm_scores)
                    .map(([score, count]) => ({ name: score, value: count }));
                
                createLineChart('rfm-scores-chart', rfmScoreData);
            }
        }
        
        // График для вкладки "Сегменты"
        if (activeTab === 'segments') {
            if (document.getElementById('segments-detail-chart')) {
                createPieChart('segments-detail-chart', segmentData);
            }
        }
    }
    
    // Публичный API
    return {
        createBarChart,
        createLineChart,
        createPieChart,
        initializeCharts
    };
})();