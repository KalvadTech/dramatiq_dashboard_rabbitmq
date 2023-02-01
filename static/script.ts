import { Chart, LineController, LineElement, CategoryScale, Tooltip, Legend, PointElement, Filler, LinearScale } from 'chart.js';
import Swal from 'sweetalert2';
import $ from 'jquery';

Chart.register(LineController, LineElement, CategoryScale, Tooltip, Legend, PointElement, Filler, LinearScale);

const elementStyle = window.getComputedStyle(document.body, null);
const elementColor = elementStyle.getPropertyValue('color');
const elementBackground = elementStyle.getPropertyValue('background');

let refreshIntervalId: ReturnType<typeof setTimeout>;

function refreshPage() {
    // refreshes the page every 5 seconds using ajax
    refreshIntervalId = setTimeout(function () {
        $.ajax({
            url: window.location.href,
            success: function (data) {
                $('#dynamic-content').html(data);
            }
        });
    }, 5000);
}

(window as any).msg_delete = (queue_name: string, message_id: string) => {
    // stops the refresh time and shows an alert to the user if the users presses yes then delete the
    // msg from the queue and refresh the page using ajax, if an error is encountered show an error alert
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
            // Create a headers object and add the Authorization header
            const headers = new Headers();
            const auth = (document.getElementById("credentials") as HTMLInputElement).value;
            headers.append('Authorization', `Basic ${auth}`);
            const options = {
                method: "DELETE",
                headers: headers
            }
            fetch("/api/queue/" + queue_name + '/message/' + message_id, options)
                .then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        Swal.fire({
                            icon: 'error', text: "There was an error deleting the message. Please try again.",
                            background: elementBackground,
                            color: elementColor,
                        });
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    Swal.fire({
                        icon: 'error', text: "There was an error deleting the message. Please try again.",
                        background: elementBackground,
                        color: elementColor,
                    });
                });
        } else {
            refreshPage();
        }
    })
}

(window as any).msg_requeue = (queue_name: string, message_id: string) => {
    // stops the refresh time and shows an alert to the user if the users presses yes then requeue the
    // msg and refresh the page using ajax, if an error is encountered show an error alert
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
            // Create a headers object and add the Authorization header
            const headers = new Headers();
            const auth = (document.getElementById("credentials") as HTMLInputElement).value;
            headers.append('Authorization', `Basic ${auth}`);
            const options = {
                method: "PUT",
                headers: headers
            }
            fetch("/api/queue/" + queue_name + '/message/' + message_id + '/requeue', options)
                .then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        Swal.fire({
                            icon: 'error', text: "There was an error requeueing deleting the message. Please try again.",
                            background: elementBackground,
                            color: elementColor,
                        });
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    Swal.fire({
                        icon: 'error', text: "There was an error requeueing deleting the message. Please try again.",
                        background: elementBackground,
                        color: elementColor,
                    });
                });
        } else {
            refreshPage();
        }
    })
}

refreshPage();

if (document.getElementById('message-count-chart')) {
    // if the chart element exists inside the page then render the chart

    const chartValue = (document.getElementById("chartdata") as HTMLInputElement).value;
    const chartData = JSON.parse(chartValue);
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
    Chart.defaults.color = elementColor;
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Current(ready)',
                data: currentDataReady,
                borderColor: 'rgba(25, 135, 84, 1)',
                backgroundColor: 'rgba(25, 135, 84, 1)',
                borderWidth: 1
            },{
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
            },{
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