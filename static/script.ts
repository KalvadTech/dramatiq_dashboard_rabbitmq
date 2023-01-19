import Chart, { ChartConfiguration, ChartItem } from 'chart.js/auto';
import * as bootstrap from 'bootstrap';

(window as any).bootstrap = bootstrap;


// Delete message
(window as any).msg_delete = (queue_name: string, message_id: string) => {
    if (confirm("Are you sure you want to delete this message?")) {
        // Send a DELETE request to the server using the fetch API
        fetch("/api/queue/" + queue_name + '/message/' + message_id, {
            method: "DELETE"
        })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("There was an error deleting the message. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("There was an error deleting the message. Please try again.");
            });
    }
}

// Requeue message
(window as any).msg_requeue = (queue_name: string, message_id: string) => {
    if (confirm("Are you sure you want to requeue this message?")) {
        // Send a PUT request to the server using the fetch API
        fetch("/api/queue/" + queue_name + '/message/' + message_id + '/requeue', {
            method: "PUT"
        })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("There was an error requeueing the message. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("There was an error requeueing the message. Please try again.");
            });
    }
}

// function refreshPage() {
//     setTimeout(function () {
//         location.reload();
//     }, 5000);
// }

// refreshPage();


const currentData = window.chart.chart_current;
const delayedData = window.chart.chart_delay;
const failedData = window.chart.chart_dead;


// create chart
const ctx = document.getElementById('message-count-chart') as HTMLCanvasElement;
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Queue 1', 'Queue 2', 'Queue 3', 'Queue 4', 'Queue 5'],
        datasets: [{
            label: 'Current',
            data: currentData,
            backgroundColor: 'rgba(42, 157, 143, 0.2)',
            borderColor: 'rgba(42, 157, 143, 1)',
            borderWidth: 1
        }, {
            label: 'Delayed',
            data: delayedData,
            backgroundColor: 'rgba(255, 193, 7, 0.2)',
            borderColor: 'rgba(255, 193, 7, 1)',
            borderWidth: 1
        }, {
            label: 'Failed',
            data: failedData,
            backgroundColor: 'rgba(255, 59, 48, 0.2)',
            borderColor: 'rgba(255, 59, 48, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});