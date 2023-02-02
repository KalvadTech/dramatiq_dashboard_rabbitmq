import { Chart, LineController, LineElement, CategoryScale, Tooltip, Legend, PointElement, Filler, LinearScale } from 'chart.js';

Chart.register(LineController, LineElement, CategoryScale, Tooltip, Legend, PointElement, Filler, LinearScale);

window.renderChart = async (queueInfo) => {
    const chartData = queueInfo.data.chart_data;
    const currentDataReady = chartData["chart_current_ready"];
    const currentDataProgress = chartData["chart_current_progress"];
    const delayedDataReady = chartData["chart_delay_ready"];
    const delayedDataProgress = chartData["chart_delay_progress"];
    const failedData = chartData["chart_dead"];
    const currentTime = new Date();
    const chartLabels = Array.from({ length: currentDataReady.length }, (_, i) => {
        const time = new Date(currentTime);
        time.setSeconds(time.getSeconds() - (currentDataReady.length - i - 1) * 5);
        return time.toLocaleTimeString();
    });


    // create chart
    const ctx = document.getElementById('message-count-chart') as HTMLCanvasElement;
    Chart.defaults.backgroundColor = 'transparent';
    Chart.defaults.borderColor = 'rgba(255,255,255, .05)';
    Chart.defaults.color = window.myApp.elementColor;
    window.myApp.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Current(ready)',
                data: currentDataReady,
                borderColor: 'rgba(25, 135, 84, 1)',
                backgroundColor: 'rgba(25, 135, 84, 1)',
                borderWidth: 1
            }, {
                label: 'Current(in progress)',
                data: currentDataProgress,
                borderColor: 'rgba(42, 157, 143, 1)',
                backgroundColor: 'rgba(42, 157, 143, 1)',
                borderWidth: 1
            }, {
                label: 'Delayed(ready)',
                data: delayedDataReady,
                borderColor: 'rgba(255, 193, 7, 1)',
                backgroundColor: 'rgba(255, 193, 7, 1)',
                borderWidth: 1
            }, {
                label: 'Delayed(in progress)',
                data: delayedDataProgress,
                borderColor: 'rgba(211, 84, 0, 1)',
                backgroundColor: 'rgba(211, 84, 0, 1)',
                borderWidth: 1
            }, {
                label: 'Failed',
                data: failedData,
                borderColor: 'rgba(255, 59, 48, 1)',
                backgroundColor: 'rgba(255, 59, 48, 1)',
                borderWidth: 1
            }]
        },
        options: {
            animation: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value: number) { if (value % 1 === 0) { return value; } }
                    }
                }

            }
        }
    });
};

window.chartUpdate = async (queueInfo) => {
    if (window.myApp.myChart) {
        const chartData = queueInfo.data.chart_data;
        const currentDataReady = chartData["chart_current_ready"];
        const currentDataProgress = chartData["chart_current_progress"];
        const delayedDataReady = chartData["chart_delay_ready"];
        const delayedDataProgress = chartData["chart_delay_progress"];
        const failedData = chartData["chart_dead"];
        const currentTime = new Date();
        const chartLabels = Array.from({ length: currentDataReady.length }, (_, i) => {
            const time = new Date(currentTime);
            time.setSeconds(time.getSeconds() - (currentDataReady.length - i - 1) * 5);
            return time.toLocaleTimeString();
        });
        window.myApp.myChart.data.labels = chartLabels;

        window.myApp.myChart.data.datasets = [{
            label: 'Current(ready)',
            data: currentDataReady,
            borderColor: 'rgba(25, 135, 84, 1)',
            backgroundColor: 'rgba(25, 135, 84, 1)',
            borderWidth: 1
        }, {
            label: 'Current(in progress)',
            data: currentDataProgress,
            borderColor: 'rgba(42, 157, 143, 1)',
            backgroundColor: 'rgba(42, 157, 143, 1)',
            borderWidth: 1
        }, {
            label: 'Delayed(ready)',
            data: delayedDataReady,
            borderColor: 'rgba(255, 193, 7, 1)',
            backgroundColor: 'rgba(255, 193, 7, 1)',
            borderWidth: 1
        }, {
            label: 'Delayed(in progress)',
            data: delayedDataProgress,
            borderColor: 'rgba(211, 84, 0, 1)',
            backgroundColor: 'rgba(211, 84, 0, 1)',
            borderWidth: 1
        }, {
            label: 'Failed',
            data: failedData,
            borderColor: 'rgba(255, 59, 48, 1)',
            backgroundColor: 'rgba(255, 59, 48, 1)',
            borderWidth: 1
        }];
        window.myApp.myChart.update();
    }
};