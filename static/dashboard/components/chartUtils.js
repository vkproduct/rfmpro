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
     * Создает столбчатую диаграмму для отображения дохода по сегментам
     * @param {string} containerId ID контейнера для графика
     * @param {Array} data Массив данных {name, revenue}
     * @param {string} title Заголовок графика
     * @returns {Object} Экземпляр графика
     */
    function createSegmentRevenueChart(containerId, data, title) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Контейнер ${containerId} не найден`);
            return null;
        }
        
        const options = {
            series: [{
                name: 'Доход',
                data: data.map(item => item.revenue)
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
                    horizontal: false,
                    columnWidth: '60%',
                    distributed: true
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280', '#059669', '#9333ea'],
            xaxis: {
                categories: data.map(item => item.name),
                labels: {
                    style: {
                        fontSize: '12px'
                    }
                }
            },
            yaxis: {
                title: {
                    text: 'Доход (₽)',
                    style: {
                        fontSize: '14px'
                    }
                },
                labels: {
                    formatter: function(val) {
                        return val.toLocaleString() + ' ₽';
                    }
                }
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val.toLocaleString() + ' ₽';
                    }
                }
            },
            title: {
                text: title || 'Доход по каждому сегменту',
                align: 'center',
                style: {
                    color: '#444'
                }
            }
        };
        
        try {
            container.innerHTML = '';
            const chart = new ApexCharts(container, options);
            chart.render();
            return chart;
        } catch (error) {
            console.error('Ошибка при создании графика дохода по сегментам:', error);
            return null;
        }
    }
    
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
                type: 'donut',  // Тип donut вместо pie
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
                        size: '60%',  // Размер отверстия
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
        
        // Формируем данные по доходу для каждого сегмента
        const segmentRevenueData = [];
        
        if (state.rfmData.customers && state.rfmData.customers.length > 0) {
            // Группируем клиентов по сегментам и суммируем их доход
            const segmentRevenues = {};
            
            state.rfmData.customers.forEach(customer => {
                const segment = customer.Customer_Segment;
                if (!segmentRevenues[segment]) {
                    segmentRevenues[segment] = 0;
                }
                segmentRevenues[segment] += customer.Monetary;
            });
            
            // Преобразуем в формат для графика
            for (const [segment, revenue] of Object.entries(segmentRevenues)) {
                segmentRevenueData.push({
                    name: segment,
                    revenue: revenue
                });
            }
            
            // Сортируем по доходу в убывающем порядке
            segmentRevenueData.sort((a, b) => b.revenue - a.revenue);
        }
        
        // Графики для вкладки "Обзор"
        if (activeTab === 'overview') {
            if (document.getElementById('segments-chart')) {
                createBarChart('segments-chart', segmentData);
            }
            
            if (document.getElementById('segment-revenue-chart') && segmentRevenueData.length > 0) {
                createSegmentRevenueChart('segment-revenue-chart', segmentRevenueData);
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
        createPieChart,
        createSegmentRevenueChart,
        initializeCharts
    };
})();