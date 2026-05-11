document.addEventListener("DOMContentLoaded", () => {
  // File Upload Logic
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const fileNameDisplay = document.getElementById("file-name");

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      fileNameDisplay.textContent =
        fileInput.files.length > 0
          ? fileInput.files[0].name
          : "No file selected";
    });
  }

  // Chart Logic
  const chartDataEl1 = document.getElementById("chart1-data");
  const { labels1, values1 } = JSON.parse(chartDataEl1.textContent);
  const chartDataEl2 = document.getElementById("chart2-data");
  const { labels2, pos, neu, neg } = JSON.parse(chartDataEl2.textContent);

  const ctx1 = document.getElementById("sentimentChart");

  new Chart(ctx1, {
    type: "pie",
    data: {
      labels: labels1, // ["Positive", "Neutral", "Negative"]
      datasets: [
        {
          label: "# of Reviews",
          data: values1,
          backgroundColor: [
            "rgba(46, 204, 113, 0.4)",
            "rgba(241, 196, 15, 0.4)",
            "rgba(231, 76, 60, 0.4)",
          ],
          borderColor: [
            "rgba(46, 204, 113, 1)",
            "rgba(241, 196, 15, 1)",
            "rgba(231, 76, 60, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {},
      plugins: {
        legend: {
          position: "bottom",
        },
      },
      responsive: true,
      maintainAspectRatio: true,
    },
  });

  const ctx2 = document.getElementById("categoryChart");
  new Chart(ctx2, {
    type: "bar",
    data: {
      labels: labels2,
      datasets: [
        {
          label: "Positive",
          data: pos,
          backgroundColor: "rgba(46, 204, 113, 0.4)",
          borderColor: "rgba(46, 204, 113, 1)",
          borderWidth: 1,
        },
        {
          label: "Neutral",
          data: neu,
          backgroundColor: "rgba(241, 196, 15, 0.4)",
          borderColor: "rgba(241, 196, 15, 1)",
          borderWidth: 1,
        },
        {
          label: "Negative",
          data: neg,
          backgroundColor: "rgba(231, 76, 60, 0.4)",
          borderColor: "rgba(231, 76, 60, 1)", // Solid border
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true },
      },
      responsive: true,
      plugins: {
        legend: { position: "top" },
      },
    },
  });

  //  Sentiment over time
  const timeDataEl = document.getElementById("time-data");

  if (timeDataEl) {
    const { labels, pos, neu, neg } = JSON.parse(timeDataEl.textContent);
    const ctxTime = document.getElementById("sentTimeChart");

    new Chart(ctxTime, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Positive",
            data: pos,
            borderColor: "rgba(46, 204, 113, 1)", // Solid Green
            backgroundColor: "rgba(46, 204, 113, 0.4)", // 0.4 Opacity Green
            tension: 0.3,
            fill: false,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: "Neutral",
            data: neu,
            borderColor: "rgba(241, 196, 15, 1)", // Solid Yellow
            backgroundColor: "rgba(241, 196, 15, 0.4)", // 0.4 Opacity Yellow
            tension: 0.3,
            fill: false,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: "Negative",
            data: neg,
            borderColor: "rgba(231, 76, 60, 1)", // Solid Red
            backgroundColor: "rgba(231, 76, 60, 0.4)", // 0.4 Opacity Red
            tension: 0.3,
            fill: false,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: "top",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
            },
            title: {
              display: true,
              text: "Review Count",
            },
          },
          x: {
            title: {
              display: true,
              text: "Month",
            },
          },
        },
      },
    });
  }
});
