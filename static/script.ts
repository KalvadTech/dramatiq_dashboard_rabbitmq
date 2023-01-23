import { Chart, LineController, LineElement, CategoryScale, Tooltip, Legend, PointElement, Filler, LinearScale } from 'chart.js';
import Swal from 'sweetalert2';

Chart.register(LineController, LineElement, CategoryScale, Tooltip, Legend, PointElement, Filler, LinearScale);

const elementStyle = window.getComputedStyle(document.body, null);
const elementColor = elementStyle.getPropertyValue('color');
const elementBackground = elementStyle.getPropertyValue('background');

let refreshIntervalId: number;

function refreshPage() {
    refreshIntervalId = setTimeout(function () {
        location.reload();
    }, 5000);
}

(window as any).msg_delete = (queue_name: string, message_id: string) => {
    clearTimeout(refreshIntervalId);
    Swal.fire({
        title: 'Are you sure you want to delete this message?',
        showDenyButton: true,
        confirmButtonText: 'Yes',
        denyButtonText: `No`,
        background: elementBackground,
        color: elementColor,
    }).then((result) => {
        if (result.isConfirmed) {
            fetch("/api/queue/" + queue_name + '/message/' + message_id, {
                method: "DELETE"
            })
                .then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        Swal.fire({ icon: 'error', text: "There was an error deleting the message. Please try again." });
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    Swal.fire({ icon: 'error', text: "There was an error deleting the message. Please try again." });
                });
        } else {
            refreshPage();
        }
    })
}

(window as any).msg_requeue = (queue_name: string, message_id: string) => {
    clearTimeout(refreshIntervalId);
    Swal.fire({
        title: 'Are you sure you want to requeue this message?',
        showDenyButton: true,
        confirmButtonText: 'Yes',
        denyButtonText: `No`,
        background: elementBackground,
        color: elementColor,
    }).then((result) => {
        if (result.isConfirmed) {
            fetch("/api/queue/" + queue_name + '/message/' + message_id + '/requeue', {
                method: "PUT"
            })
                .then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        Swal.fire({ icon: 'error', text: "There was an requeueing deleting the message. Please try again." });
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    Swal.fire({ icon: 'error', text: "There was an requeueing deleting the message. Please try again." });
                });
        } else {
            refreshPage();
        }
    })
}

refreshPage();


const chartValue = (document.getElementById("chartdata") as HTMLInputElement).value;
let chartData = JSON.parse(chartValue);
let currentData = chartData["chart_current"];
let delayedData = chartData["chart_delay"];
let failedData = chartData["chart_dead"];
const currentTime = new Date();
const chartLabels = Array.from({ length: currentData.length }, (_, i) => {
    const time = new Date(currentTime);
    time.setSeconds(time.getSeconds() - (currentData.length - i - 1) * 5);
    return time.toLocaleTimeString();
});


// create chart
const ctx = document.getElementById('message-count-chart') as HTMLCanvasElement;
Chart.defaults.backgroundColor = 'transparent';
Chart.defaults.borderColor = 'rgba(255,255,255, .05)';
Chart.defaults.color = elementColor;
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartLabels,
        datasets: [{
            label: 'Current',
            data: currentData,
            borderColor: 'rgba(42, 157, 143, 1)',
            backgroundColor: 'rgba(42, 157, 143, 1)',
            borderWidth: 1
        }, {
            label: 'Delayed',
            data: delayedData,
            borderColor: 'rgba(255, 193, 7, 1)',
            backgroundColor: 'rgba(255, 193, 7, 1)',
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
