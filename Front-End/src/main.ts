import * as echarts from 'echarts';

let currentGranularity = "5sec";
const details = document.querySelector("#granularity details") as HTMLDetailsElement;
const granularityButton = document.querySelector("#granularity summary a")!;
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

async function fetchData(granularity = "5sec") {
    try {
        const res = await fetch(`http://localhost:8000/crowd_logs?granularity=${granularity}`);
        const json = await res.json();

        const xData = json.map((item: any) =>
            new Date(item.time).toLocaleTimeString()
        );

        const yData = json.map((item: any) => item.value);


        myChart.setOption({
            title: { text: "Crowd Count" },
            tooltip: { trigger: "axis" },
            xAxis: {
                type: "category",
                data: xData
            },
            yAxis: {
                type: "value"
            },
            series: [
                {
                    type: "line",
                    data: yData,
                    smooth: true
                }
            ]
        });
    } catch (e) {
        console.log("Fetch error:", e);
    }
}

async function fetchSummary() {
    try {
        const res = await fetch("http://localhost:8000/summary");
        const data = await res.json();

        document.getElementById("last30")!.textContent =
            data.last_30_sec.toFixed(3);

        document.getElementById("peakToday")!.textContent =
            data.peak_today.toFixed(3);

        document.getElementById("avgHour")!.textContent =
            data.avg_per_hour.toFixed(3);

        document.getElementById("totalToday")!.textContent =
            data.total_today.toFixed(3);
    } catch (e) {
        console.error("Summary fetch error", e);
    }
}
// default load
fetchData("5sec");
fetchSummary();   

// Update setiap 5 detik
setInterval(() => {
    fetchSummary()
    fetchData(currentGranularity);
}, 5000);


// dropdown click handler
document.querySelectorAll("#granularity ul a").forEach(el => {
    el.addEventListener("click", (e) => {
        e.preventDefault();

        const target = (e.currentTarget as HTMLElement);
        const g = target.dataset.value;
        if (!g) return;

        granularityButton.textContent = g;
        currentGranularity = g;
        fetchData(g);

        // 🔥 tutup dropdown dengan benar
        details.removeAttribute("open");
    });
});

document.querySelector("#downloadCSVButton")?.addEventListener("click", () => {
    window.open("http://localhost:8000/export_csv", "_blank");
})