import * as echarts from 'echarts';

const myChart = echarts.init(document.getElementById('chart'));

const option = {
    title: { text: 'Crowd Count Over Time' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [
        {
            type: 'line',
            smooth: true,
            data: []
        }
    ]
};

myChart.setOption(option);

async function fetchData() {
    try {
        const res = await fetch("http://localhost:8000/crowd_logs");
        const json = await res.json();

        const xData = json.map((item: any) => new Date(item.timestamp * 1000).toLocaleTimeString());
        const yData = json.map((item: any) => item.count);

        myChart.setOption({
            xAxis: { data: xData },
            series: [{ data: yData }]
        });
    } catch (e) {
        console.log("Fetch error:", e);
    }
}

// Update setiap 5 detik
setInterval(fetchData, 5000);

// First render
fetchData();
