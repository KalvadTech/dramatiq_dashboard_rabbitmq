
import "./queue.ts";
import "./chart.ts";

const elementStyle = window.getComputedStyle(document.body, null);

window.myApp = {

  elementColor: elementStyle.getPropertyValue('color'),
  isHomePage: Boolean(document.getElementById('message-count-chart')),
  refreshIntervalId: undefined,
  elementBackground: elementStyle.getPropertyValue('background'),

};

window.queueInfo = async () => {
  const headers = new Headers();
  const auth = (document.getElementById("credentials") as HTMLInputElement).value;
  headers.append('Authorization', `Basic ${auth}`);
  const options = {
    method: "GET",
    headers: headers
  };
  const res = await fetch("/api/queue", options);
  const queueData = await res.json();
  return queueData;
};

window.queueData = async (queueInfo) => {
  const queuesTbody = document.querySelector("#queue_stats_table");
  if (queuesTbody) queuesTbody.innerHTML = "";
  Object.entries(queueInfo.data.list_of_queues).forEach((key) => {
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
            <td>
            <button type="button" class="btn border">
            <a
                href="${window.location.href}queue/${key[0]}/current"
                >
            <i class="bi bi-info"></i></a>
              </button>
            </td>
          </tr>`;
  });
};

window.refreshPage = () => {

  if (!window.myApp.isHomePage) {
    // refreshes the page every 5 seconds
    window.myApp.refreshIntervalId = setInterval(async function () {
      const res = await fetch(window.location.href);
      const contentElement = document.querySelector("#dynamic-content");
      if (contentElement) {
        contentElement.innerHTML = await res.text();
      }
    }, 5000);
  }
  else {
    window.myApp.refreshIntervalId = setInterval(async function () {
      const queueData: any = await window.queueInfo();
      window.chartUpdate(queueData);
      window.queueData(queueData);
    }, 5000);
  }
};

window.refreshPage();


if (window.myApp.isHomePage) {
  // Render home page
  async function makePage() {
    const queueData: any = await window.queueInfo();
    window.renderChart(queueData);
    window.queueData(queueData);
  };
  makePage();
};