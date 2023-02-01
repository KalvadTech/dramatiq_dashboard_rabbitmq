
import "./queue.ts";
import "./chart.ts";

const elementStyle = window.getComputedStyle(document.body, null);

window.myApp = {

    elementColor: elementStyle.getPropertyValue('color'),
    isHomePage: Boolean(document.getElementById('message-count-chart')),
    refreshIntervalId: undefined,
    elementBackground: elementStyle.getPropertyValue('background'),

};

window.queueData = async () => {
    const headers = new Headers();
    const auth = (document.getElementById("credentials") as HTMLInputElement).value;
    headers.append('Authorization', `Basic ${auth}`);
    const options = {
        method: "GET",
        headers: headers
    };
    const res = await fetch("/api/queue", options);
    const queueData = await res.json();

    queueData.data.all_messages_in_dead_letter_queues;
    queueData.data.all_messages_in_dead_letter_queues;

    const queuesTbody = document.querySelector("#queue_stats_table");
    if (queuesTbody) queuesTbody.innerHTML = "";
    Object.entries(queueData.data.list_of_queues).forEach((key, value) => {
        if (queuesTbody) queuesTbody.innerHTML += `            
            <tr>
            <td>
              <a
                href="${window.location.href}queue/${key[0]}/current"
                >${key[0]}</a
              >
            </td>
            <td class="text-success">
              <span id="current_message_count">
              ${key[1].current_message_count_ready}(${key[1].current_message_count_progress})
              </span>
            </td>
            <td class="text-warning">
              <span id="delay_message_count">
              ${key[1].delay_message_count_ready}(${key[1].delay_message_count_progress})
              </span>
            </td>
                  <td class="text-danger"><span id="dead_message_count">${key[1].dead_message_count}</span></td>
          </tr>`;
    });
    const queuesStats = document.querySelector("#queue_stats");

    if (queuesStats) queuesStats.innerHTML = `
    <p>    
    The number of messages in all current queues that are ready:
    ${queueData.data.all_messages_in_queues_ready}
  </p>
  <p>
    The number of messages in all current queues that are in progress: 
    ${queueData.data.all_messages_in_queues_progress}

  </p>
  <p>
    The number of messages in all delay queues that are ready: 
    ${queueData.data.all_messages_in_delay_queues_ready}

  </p>
  <p>
    The number of messages in all current queues that are in progress: 
    ${queueData.data.all_messages_in_delay_queues_progress}

  </p>
  <p>
    The number of messages in all dead queues is: 
    ${queueData.data.all_messages_in_dead_letter_queues}
  </p>`;

};

window.refreshPage = () => {

    if (!window.myApp.isHomePage) {
        // refreshes the page every 5 seconds
        window.myApp.refreshIntervalId = setInterval(async function () {
            console.log("refreshed firted");
            const res = await fetch(window.location.href);
            const contentElement = document.querySelector("#dynamic-content");
            if (contentElement) {
                contentElement.innerHTML = await res.text();
            }
        }, 5000);
    }
    else {
        window.myApp.refreshIntervalId = setInterval(async function () {
            window.chartUpdate();
            window.queueData();
        }, 5000);
    }
};

window.refreshPage();


if (window.myApp.isHomePage) {
    // if the chart element exists inside the page then render the chart
    window.renderChart();
    window.queueData();
};