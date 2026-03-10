// charts.js: handles Chart.js graphs for analytics (weight, strength, calories, protein, goal progress). fetches data from Flask analytics endpoints; period buttons update charts.
//
// Line Chart Implementation Reference:
// Source: https://codepen.io/ilovepku/pen/PoobMGL
//
// EDITS MADE TO LINE CHARTS:
// 1. Removed Firebase/Firestore integration - replaced with Flask REST API endpoints
// 2. Changed from D3.js library to Chart.js library for simpler implementation
// 3. Removed D3-specific code (d3.scaleTime, d3.line, d3.axisBottom, etc.)
// 4. Simplified data fetching: using fetch() API instead of Firebase real-time listeners
// 5. Changed chart types:
//    - Weight chart: line chart showing weight progression over time
//    - Strength chart: multi-line chart showing different exercises' weight progression
//    - Calories chart: line chart showing daily/weekly/monthly/yearly calorie intake
//    - Protein chart: line chart showing daily/weekly/monthly/yearly protein intake
// 6. Added period filtering (daily, weekly, monthly, yearly) with buttons
// 7. Removed interactive hover effects (dotted lines) - Chart.js handles this natively
// 8. Integrated with Flask backend endpoints:
//    - /analytics/weight
//    - /analytics/strength
//    - /analytics/calories?period=X
//    - /analytics/protein?period=X
// 9. Added chart instance management to allow updating charts when period changes
//
// WHY: The original template used D3.js with Firebase for a real-time activity tracker.
// We needed simpler line charts integrated with our SQLite database via Flask, so we
// switched to Chart.js which is easier to use and better suited for our REST API architecture.
// We also needed multiple chart types (weight, strength, calories, protein) with period
// filtering, which Chart.js handles more easily than the original D3 implementation.

// Store chart instances for updating
var chartInstances = {};

document.addEventListener("DOMContentLoaded", function () {
    initializeCharts();
    setupViewButtons();
    initializeGoalProgressCharts();
    loadStrengthExercises();
});

function setupViewButtons() {
    document.querySelectorAll('.view-period-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.dataset.period;
            const chartType = this.dataset.chart;
            
            // Update active state
            document.querySelectorAll(`[data-chart="${chartType}"]`).forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update chart
            updateChart(chartType, period);
        });
    });
}

function initializeCharts() {
    // Weight chart
    loadWeightChart('weekly');
    
    // Strength chart
    loadStrengthChart('weekly');
    
    // Calories chart
    loadCaloriesChart('weekly');
    
    // Protein chart
    loadProteinChart('weekly');
}

function updateChart(chartType, period) {
    switch(chartType) {
        case 'weight':
            loadWeightChart(period);
            break;
        case 'strength':
            loadStrengthChart(period);
            break;
        case 'calories':
            loadCaloriesChart(period);
            break;
        case 'protein':
            loadProteinChart(period);
            break;
    }
}

// 1. Weight progression line chart
function loadWeightChart(period) {
    var weightCanvas = document.getElementById("weightChart");
    if (!weightCanvas) return;
    
    fetch("/analytics/weight?period=" + (period || "weekly"))
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = [];
            var weights = [];

            data.forEach(function (item) {
                labels.push(item.date);
                weights.push(item.weight);
            });
            weightCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px";

            if (chartInstances.weightChart) {
                chartInstances.weightChart.destroy();
            }

            chartInstances.weightChart = new Chart(weightCanvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Weight (kg)",
                            data: weights,
                            borderColor: "rgb(75, 192, 192)",
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            fill: true,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false,
                        },
                    },
                },
            });
        })
        .catch(function () {
            console.log("Could not load weight data.");
        });
}

// 2. Strength progression: filter by exercise, y = weight/rep (gym) or duration (cardio)
function loadStrengthChart(period) {
    var strengthCanvas = document.getElementById("strengthChart");
    if (!strengthCanvas) return;
    var exerciseSelect = document.getElementById("strengthExerciseSelect");
    var exerciseName = exerciseSelect ? exerciseSelect.value : "";
    var url = "/analytics/strength";
    var sep = "?";
    if (period) {
        url += sep + "period=" + encodeURIComponent(period);
        sep = "&";
    }
    if (exerciseName) {
        url += sep + "exercise=" + encodeURIComponent(exerciseName);
    }
    fetch(url)
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = [];
            var yValues = [];
            var yAxisLabel = "Value";
            if (data.length > 0) {
                var ex = data[0];
                yAxisLabel = ex.exercise_type === "cardio" ? "Duration (min)" : "Weight per Rep (kg)";
                (ex.data_points || []).forEach(function (point) {
                    labels.push(point.date);
                    yValues.push(point.y_value != null ? point.y_value : (point.weight || 0));
                });
            }
            strengthCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px";
            if (chartInstances.strengthChart) {
                chartInstances.strengthChart.destroy();
            }
            chartInstances.strengthChart = new Chart(strengthCanvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: yAxisLabel,
                        data: yValues,
                        borderColor: "rgb(75, 192, 192)",
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        fill: true,
                    }],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: yAxisLabel },
                        },
                    },
                },
            });
        })
        .catch(function () {
            console.log("Could not load strength data.");
        });
}

function loadStrengthExercises() {
    fetch("/exercise/list")
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var select = document.getElementById("strengthExerciseSelect");
            if (!select) return;
            var current = select.value;
            select.innerHTML = "";
            var opt = document.createElement("option");
            opt.value = "";
            opt.text = "All exercises";
            select.appendChild(opt);
            (data || []).forEach(function (ex) {
                var option = document.createElement("option");
                option.value = ex.exercise_name;
                option.text = ex.exercise_name;
                select.appendChild(option);
            });
            if (current) select.value = current;
            select.onchange = function () {
                var activeBtn = document.querySelector('.view-period-btn[data-chart="strength"].active');
                var p = activeBtn ? activeBtn.dataset.period : 'weekly';
                loadStrengthChart(p);
            };
        })
        .catch(function () {
            console.log("Could not load exercises.");
        });
}

// 3. Calories chart: spent (orange), gained (green), net (pink)
function loadCaloriesChart(period) {
    var caloriesCanvas = document.getElementById("caloriesChart");
    if (!caloriesCanvas) return;
    
    fetch("/analytics/calories?period=" + (period || "weekly"))
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = [];
            var spent = [];
            var gained = [];
            var net = [];
            data.forEach(function (item) {
                labels.push(item.period);
                spent.push(item.spent != null ? item.spent : 0);
                gained.push(item.gained != null ? item.gained : 0);
                net.push(item.net != null ? item.net : 0);
            });
            caloriesCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px";
            if (chartInstances.caloriesChart) {
                chartInstances.caloriesChart.destroy();
            }
            chartInstances.caloriesChart = new Chart(caloriesCanvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [
                        { label: "Calories Spent (cal)", data: spent, borderColor: "rgb(255, 165, 0)", fill: false },
                        { label: "Calories Gained (cal)", data: gained, borderColor: "rgb(34, 139, 34)", fill: false },
                        { label: "Net Calories (cal)", data: net, borderColor: "rgb(255, 192, 203)", fill: false },
                    ],
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: false } },
                },
            });
        })
        .catch(function () {
            console.log("Could not load calories data.");
        });
}

// 4. Protein intake line chart
function loadProteinChart(period) {
    var proteinCanvas = document.getElementById("proteinChart");
    if (!proteinCanvas) return;
    
    fetch("/analytics/protein?period=" + period)
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = [];
            var protein = [];

            data.forEach(function (item) {
                labels.push(item.period);
                protein.push(item.protein);
            });
            proteinCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px";
            if (chartInstances.proteinChart) {
                chartInstances.proteinChart.destroy();
            }

            chartInstances.proteinChart = new Chart(proteinCanvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Protein (g)",
                            data: protein,
                            borderColor: "rgb(54, 162, 235)",
                            backgroundColor: "rgba(54, 162, 235, 0.2)",
                            fill: true,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            });
        })
        .catch(function () {
            console.log("Could not load protein data.");
        });
}

// 5. Circular progress charts for goals
// Source: https://codepen.io/dianastanciu/pen/bGbwVNr
//
// EDITS MADE:
// 1. Removed hardcoded HTML structure - now dynamically generates SVG circles for each goal
// 2. Changed from fixed animation values to dynamic calculation:
//    - Calculate circumference based on radius (64)
//    - Calculate stroke-dashoffset based on actual goal progress_percent from API
//    - Use JavaScript to set stroke-dashoffset style instead of CSS animations
// 3. Integrated with Flask backend: fetches goals from /analytics/goals endpoint
// 4. Changed display values:
//    - Top value shows progress percentage (0-100%) instead of fixed "2758"
//    - Bottom value shows goal description (truncated to 15 chars) instead of "cal"
// 5. Removed multiple circle sizes (circle-big, circle-small) - using single size for all goals
// 6. Added container generation for multiple goals (one chart per goal)
// 7. Changed color scheme: kept #27E1AE for progress, #000000 for shadow (from original)
//
// WHY: The original template was a static demo with fixed values. We needed to:
// - Display multiple goals dynamically from our database
// - Show actual progress percentages calculated from goal current_value vs target_value
// - Integrate with our Flask analytics API
// - Make it responsive to real user data rather than hardcoded examples
function initializeGoalProgressCharts() {
    fetch("/analytics/goals")
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var container = document.getElementById("goalsCircularContainer");
            if (!container) return;
            
            container.innerHTML = "";
            
            if (data.length === 0) {
                container.innerHTML = "<p>No goals set yet.</p>";
                return;
            }

            data.forEach(function (goal) {
                var progressPercent = Math.min(goal.progress_percent, 100);
                var circumference = 2 * Math.PI * 64; // radius is 64
                var offset = circumference - (progressPercent / 100) * circumference;
                
                var circleHtml = `
                    <div class="circular-progress-container">
                        <div class="circular-progress">
                            <svg height="150" width="150">
                                <circle cx="80" cy="74" r="64" class="line-shadow" stroke="#000000" stroke-width="10" fill="none"></circle>
                                <circle cx="80" cy="74" r="64" class="line" stroke="#27E1AE" stroke-width="10" fill="none" 
                                    stroke-dasharray="${circumference}" 
                                    stroke-dashoffset="${circumference}"
                                    style="stroke-dashoffset: ${offset}; transition: stroke-dashoffset 1s ease;"></circle>
                            </svg>
                            <div class="info">
                                <span class="info__top">${progressPercent.toFixed(0)}%</span>
                                <span class="info__bottom">${goal.description.substring(0, 15)}${goal.description.length > 15 ? '...' : ''}</span>
                            </div>
                        </div>
                    </div>
                `;
                
                container.innerHTML += circleHtml;
            });
        })
        .catch(function () {
            console.log("Could not load goals data.");
        });
}
