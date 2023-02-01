import { Chart } from 'chart.js';
export { };
declare global {
    interface Window {
        myApp: {
            elementColor: string,
            isHomePage: Boolean,
            refreshIntervalId?: ReturnType<typeof setTimeout>,
            elementBackground: string,
            myChart?: Chart,
        };
        refreshPage: () => void;
        renderChart: () => void;
        chartUpdate: () => void;
        queueData: () => void;
    }
}