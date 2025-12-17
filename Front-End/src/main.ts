import * as echarts from 'echarts';

let currentGranularity = "5sec";
const details = document.querySelector("#granularity details") as HTMLDetailsElement;
const granularityButton = document.querySelector("#granularity summary a")!;
const chartEl = document.getElementById('chart')!;
const myChart = echarts.init(chartEl);
let avgHourValue: number | null = null;

const option = {
    title: { text: 'Crowd Count Over Time' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [
        {
            type: 'line',
            smooth: true,
            data: []
        }
    ],
    dataZoom: [
        {
            type: 'inside',  // scroll drag di chart
            start: 0,
            end: 100
        },
        {
            type: 'slider',  // scrollbar bawah chart
            start: 0,
            end: 100
        }
    ]
};

myChart.setOption(option);

function toWIB(timestamp: number): string {
    // jika timestamp > 10^12 kemungkinan sudah ms
    if (timestamp < 1e12) timestamp *= 1000; 
    const date = new Date(timestamp);
    date.setHours(date.getUTCHours() + 7); // WIB
    return date.toLocaleTimeString('id-ID', { hour12: false });
}


async function fetchData(granularity = "5sec") {
    try {
        const res = await fetch(`http://localhost:8000/crowd_logs?granularity=${granularity}`);
        const json = await res.json();

        const xData = json.map((item: any) => toWIB(item.time));
        const yData = json.map((item: any) => item.value);

        myChart.setOption({
            xAxis: { data: xData },
            series: [
                {
                    data: yData,
                    markLine: avgHourValue !== null ? {
                        silent: true,
                        symbol: "none",
                        label: {
                            show: true,
                            formatter: `Avg Hour: ${avgHourValue.toFixed(2)}`,
                            position: "end"
                        },
                        lineStyle: {
                            type: "dashed",
                            width: 2,
                            color: "#fff"
                        },
                        data: [{ yAxis: avgHourValue }]
                    } : undefined
                }
            ]
        });
    } catch (e) {
        console.error("Fetch error:", e);
    }
}

async function fetchSummary() {
    try {
        const res = await fetch("http://localhost:8000/summary");
        const data = await res.json();

        document.getElementById("last30")!.textContent = data.five_sec;
        document.getElementById("peakToday")!.textContent = data.peak_today;
        avgHourValue = data.avg_per_hour;
        document.getElementById("avgHour")!.textContent = avgHourValue!.toFixed(3);
        document.getElementById("totalToday")!.textContent = data.lowest_today;
    } catch (e) {
        console.error("Summary fetch error", e);
    }
}

// default load
fetchData(currentGranularity);
fetchSummary();

// update setiap 5 detik
setInterval(() => {
    fetchSummary();
    fetchData(currentGranularity);
}, 5000);

// dropdown click handler
document.querySelectorAll("#granularity ul a").forEach(el => {
    el.addEventListener("click", (e) => {
        e.preventDefault();
        const target = e.currentTarget as HTMLElement;
        const g = target.dataset.value;
        if (!g) return;

        granularityButton.textContent = g;
        currentGranularity = g;
        fetchData(g);
        details.removeAttribute("open");
    });
});

document.querySelector("#downloadCSVButton")?.addEventListener("click", () => {
    window.open("http://localhost:8000/export_csv", "_blank");
});
