// Income Chart (Line Chart)
const incomeChart = new CustomChartJs({
    selector: '#incomeChart',
    options: () => {
        return {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    data: [0, 15, 10, 20, 18, 25, 30],
                    backgroundColor: ins('chart-primary-rgb', 0.6),
                    borderColor: ins('chart-primary'),
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: {
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        display: false,
                        grid: { display: false }
                    }
                }
            }
        };
    }
});


const pageViewsChart = new CustomChartJs({
    selector: '#pageViewsChart',
    options: () => {
        return {
            type: 'bar',
            data: {
                labels: ['1', '2', '3', '4', '5', '6'],
                datasets: [{
                    data: [4, 4, 5, 6, 8, 5],
                    backgroundColor: ins('chart-primary'),
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        display: false,
                        grid: { display: false }
                    }
                }
            }
        };
    }
});

const todayIncomePieChart = new CustomChartJs({
    selector: '#todayIncomePieChart',
    options: () => {
        return {
            type: 'pie',
            data: {
                labels: ['Data 1', 'Data 2', 'Data 3', 'Data 4'],
                datasets: [{
                    data: [25, 30, 20, 25],
                    backgroundColor: [
                        ins('chart-primary'),
                        ins('chart-secondary'),
                        ins('chart-gray'),
                        ins('chart-dark')
                    ],
                    borderColor: '#fff',
                    borderWidth: 0
                }]
            },
            options: {
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: function (ctx) {
                                return `${ctx.label}: ${ctx.parsed}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: { display: false, grid: { display: false }, ticks: { display: false } },
                    y: { display: false, grid: { display: false }, ticks: { display: false } }
                }
            }
        };
    }
});

const todayIncomeChart = new CustomChartJs({
    selector: '#todayIncomeChart',
    options: () => {
        return {
            type: 'line',
            data: {
                labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
                datasets: [{
                    label: 'Income',
                    data: [30, 18, 28, 35, 33, 40, 25, 29, 41],
                    backgroundColor: ins('chart-primary-rgb', 0.6),
                    borderColor: ins('chart-primary'),
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: {
                        ticks: {
                            color: ins('secondary-color'),
                            font: { family: getComputedStyle(document.body).fontFamily.trim() }
                        },
                        grid: { display: true, drawBorder: false, color: ins('chart-border-color') }
                    },
                    y: {
                        ticks: {
                            color: ins('secondary-color'),
                            font: { family: getComputedStyle(document.body).fontFamily.trim() }
                        },
                        grid: { display: true, drawBorder: false, color: ins('chart-border-color') }
                    }
                }
            }
        };
    }
});
