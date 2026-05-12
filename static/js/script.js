document.addEventListener("DOMContentLoaded", () => {
  // File upload logic
  const fileInput = document.getElementById("file-input");
  const fileNameDisplay = document.getElementById("file-name");
  const hint = document.querySelector(".hint");

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      fileNameDisplay.textContent =
        fileInput.files.length > 0
          ? fileInput.files[0].name
          : "No file selected";
      hint.classList.add("hidden");
    });
  }

  // Async analysis logic
  const loader = document.getElementById("loading-state");
  const dashboard = document.getElementById("dashboard-content");
  const statusText = document.getElementById("status-text");

  if (loader) {
    fetch("/analyze")
      .then((response) => {
        if (!response.ok)
          throw new Error("Analysis failed. Please check your CSV format.");
        return response.json();
      })
      .then((data) => {
        loader.style.display = "none";
        dashboard.style.display = "block";

        // Update stats
        if (data.total_count !== undefined) {
          document.getElementById("total-reviews").innerText = data.total_count;
        }
        if (data.avg_score !== undefined) {
          document.getElementById("avg-score-display").innerText =
            data.avg_score;
        }

        // Render charts
        renderSentimentPie(data.pie);
        renderCategoryStackedBar(data.stacked);

        if (data.time_series && data.time_series.has_time) {
          renderTimeLineChart(data.time_series);
        }

        // Update product list
        updateRankingsUI(data);
      })
      .catch((err) => {
        console.error("Error:", err);
        statusText.innerHTML = `<span style="color: #e74c3c;">${err.message}</span>`;
      });
  }
});

let rankingsData = null;

function updateRankingsUI(data) {
  rankingsData = data.rankings;
  renderList("best", "overall");
  renderList("worst", "overall");
}

function renderList(type, mode) {
  const container = document.getElementById(`${type}-products-list`);
  if (!container || !rankingsData) return;

  container.innerHTML = "";

  if (mode === "overall") {
    const products = rankingsData.overall[type];
    if (!products || products.length === 0) {
      container.innerHTML = "<p class='no-data'>No products met threshold.</p>";
      return;
    }

    products.forEach((name, index) => {
      container.innerHTML += `
        <div class="product-item">
            <span class="rank-num">#${index + 1}</span>
            <span class="product-name">${name}</span>
        </div>`;
    });
  } else {
    const catEntries = Object.entries(rankingsData.by_category);
    if (catEntries.length === 0) {
      container.innerHTML = "<p class='no-data'>No category data.</p>";
      return;
    }

    catEntries.forEach(([cat, items]) => {
      const productNames = items[type].join(", ");
      if (productNames) {
        container.innerHTML += `
            <div class="category-group">
                <strong class="cat-label">${cat}</strong>
                <div class="product-item">${productNames}</div>
            </div>`;
      }
    });
  }
}

function toggleRankings(type, mode, event) {
  renderList(type, mode);

  if (!event || !event.currentTarget) {
    console.warn("Toggle function called without a valid event object.");
    return;
  }

  const btn = event.currentTarget;
  const container = btn.parentElement;

  if (container) {
    container
      .querySelectorAll(".tab-btn")
      .forEach((s) => s.classList.remove("active"));
    btn.classList.add("active");
  }
}

// Chart rendering functions
function renderSentimentPie(pieData) {
  const ctx = document.getElementById("sentimentChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: pieData.labels,
      datasets: [
        {
          data: pieData.values,
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
      plugins: { legend: { position: "bottom" } },
      responsive: true,
      maintainAspectRatio: true,
    },
  });
}

function renderCategoryStackedBar(stackedData) {
  const ctx = document.getElementById("categoryChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: stackedData.labels,
      datasets: [
        {
          label: "Positive",
          data: stackedData.pos,
          backgroundColor: "rgba(46, 204, 113, 0.4)",
          borderColor: "rgba(46, 204, 113, 1)",
          borderWidth: 1,
        },
        {
          label: "Neutral",
          data: stackedData.neu,
          backgroundColor: "rgba(241, 196, 15, 0.4)",
          borderColor: "rgba(241, 196, 15, 1)",
          borderWidth: 1,
        },
        {
          label: "Negative",
          data: stackedData.neg,
          backgroundColor: "rgba(231, 76, 60, 0.4)",
          borderColor: "rgba(231, 76, 60, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

function renderTimeLineChart(timeData) {
  const ctx = document.getElementById("sentTimeChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: timeData.labels,
      datasets: [
        {
          label: "Positive",
          data: timeData.pos,
          borderColor: "rgba(46, 204, 113, 0.4)",
          backgroundColor: "rgba(46, 204, 113, 0.4)",
          tension: 0.3,
          fill: false,
        },
        {
          label: "Neutral",
          data: timeData.neu,
          borderColor: "rgba(241, 196, 15, 0.4)",
          backgroundColor: "rgba(241, 196, 15, 0.4)",
          tension: 0.3,
          fill: false,
        },
        {
          label: "Negative",
          data: timeData.neg,
          borderColor: "rgba(231, 76, 60, 0.4)",
          backgroundColor: "rgba(231, 76, 60, 0.4)",
          tension: 0.3,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { lineWidth: 1, padding: 20 } },
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: "Reviews" } },
        x: { title: { display: true, text: "Month" } },
      },
    },
  });
}
