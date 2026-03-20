// handles graphs for analytics (weight, strength, calories, protein, goal progress
// fetches data from Flask analytics endpoints (Flask /analytics/) and period buttons update time view of charts


// line chart graphs from:
// Source: https://codepen.io/ilovepku/pen/PoobMGL
//
// edits i made:
// 1. removed firebase/firestore and replaced with Flask REST API endpoints to integrate with my program
// 2. simplified data fetching using fetch()
// 3. changed chart types/ purpose for multiple uses:
//    - Weight chart: weight progression over time
//    - Strength chart: weight progression in a selected exercise (x axis change respective to exercise type weight per rep or duration)
//    - Calories chart: calorie intake over time with spent, intake and net.
//    - Protein chart: protein intake over time
// 4. time period button (daily, weekly, monthly, yearly) changing time scale of graph
// 5. removed interactive hover effects
// 6. Integrated it with the Flask backend endpoints for data fetching:
//    - /analytics/weight
//    - /analytics/strength
//    - /analytics/calories?period=X
//    - /analytics/protein?period=X
// 7. added chart instance management to allow updating charts when period changes
// 8. in case of errors added lines to do nothing to avoid program crashing



var chartInstances = {}; // keeps reference of chart instances to to delete and redraw graphs when period changes

document.addEventListener("DOMContentLoaded", function () { // initialises charts and goal progress charts
    initialiseCharts(); // initialises the charts
    setupViewButtons(); // sets up the view buttons for the charts
    initialiseGoalProgressCharts(); // initialises the goal progress charts
    loadStrengthExercises(); // loads the exercises for the strength chart
});

function setupViewButtons() { // sets up the view buttons for the charts with changing time period
    document.querySelectorAll('.view-period-btn').forEach(btn => { // for each button in the view-period-btn class
        btn.addEventListener('click', function() { // when the button is clicked
            const period = this.dataset.period; //  period = daily/weekly/monthly/yearly
            const chartType = this.dataset.chart; // chartType = weight/strength/calories/protein
            document.querySelectorAll(`[data-chart="${chartType}"]`).forEach(b => b.classList.remove('active')); // removes the active class from the other buttons
            this.classList.add('active'); // adds the new active class to the clicked button
            updateChart(chartType, period); // updates the chart with the new period
        });
    });
}

function initialiseCharts() { // initialises the charts (default to weekly)
    // weight chart
    loadWeightChart('weekly');
    
    // strength chart
    loadStrengthChart('weekly');
    
    // calories chart
    loadCaloriesChart('weekly');
    
    // protein chart
    loadProteinChart('weekly');
}

function updateChart(chartType, period) { // updates the chart with the new period
    switch(chartType) {
        case 'weight':
            loadWeightChart(period); // reloads the weight chart with the new period
            break;
        case 'strength':
            loadStrengthChart(period); // reloads the strength chart with the new period
            break;
        case 'calories':
            loadCaloriesChart(period); // reloads the calories chart with the new period
            break;
        case 'protein':
            loadProteinChart(period); // reloads the protein chart with the new period
            break;
    }
}

// 1. Weight progression line chart: y axis = weight (kg) x axis = date
function loadWeightChart(period) { // loads the weight chart with the new period
    var weightCanvas = document.getElementById("weightChart"); // gets the weight chart canvas
    if (!weightCanvas) return; // if the weight chart canvas is not found, return and do nothing
    
    fetch("/analytics/weight?period=" + (period || "weekly")) // fetches the weight data from the Flask backend
        .then(function (response) {
            return response.json(); // converts the response to JSON
        })
        .then(function (data) {
            var labels = []; // creates an empty list to store the labels
            var weights = []; // creates an empty list to store the weights

            data.forEach(function (item) { // loops through the data
                labels.push(item.date); // adds the date to the labels list
                weights.push(item.weight); // adds the weight to the weights list
            });
            weightCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px"; // sets the minimum width of the weight chart canvas
            if (chartInstances.weightChart) chartInstances.weightChart.destroy(); // deletes the existing weight chart instance
            chartInstances.weightChart = new Chart(weightCanvas, { // creates a new weight chart instance
                type: "line", // graph style from the Source
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

// 2. strength progression line chart: filter by exercise, y axis = weight per rep (gym) or duration (cardio)
function loadStrengthChart(period) { // loads the strength chart with the new period
    var strengthCanvas = document.getElementById("strengthChart"); // gets the strength chart canvas
    if (!strengthCanvas) return; // if the strength chart canvas is not found, return and do nothing
    var exerciseSelect = document.getElementById("strengthExerciseSelect"); // gets the exercise select dropdown
    var exerciseName = exerciseSelect ? exerciseSelect.value : ""; // gets the exercise name from the exercise select dropdown
    var url = "/analytics/strength"; // URL for the strength data
    var sep = "?"; // separator for the URL
    if (period) { // if there is a period
        url += sep + "period=" + encodeURIComponent(period); // adds the period to the URL
        sep = "&"; // separator for the URL
    }
    if (exerciseName) { // if there is an exercise name
        url += sep + "exercise=" + encodeURIComponent(exerciseName); // adds the exercise name to the URL
    }
    fetch(url) // fetches the strength data from the Flask backend
        .then(function (response) {
            return response.json(); // converts the response to JSON
        })
        .then(function (data) {
            var labels = []; // creates an empty list to store the labels
            var yValues = []; // creates an empty list to store the y values   
            var yAxisLabel = "Value"; // label for the y axis
            if (data.length > 0) { // if there is data
                var ex = data[0]; // gets the first exercise from the data
                yAxisLabel = ex.exercise_type === "cardio" ? "Duration (min)" : "Weight per Rep (kg)"; // sets the y axis label based on the exercise type
                (ex.data_points || []).forEach(function (point) { // loops through the data points
                    labels.push(point.date); // adds the date to the labels list
                    yValues.push(point.y_value != null ? point.y_value : (point.weight || 0)); // adds the y value to the y values list
                });
            }
            strengthCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px"; // sets the minimum width of the strength chart canvas
            if (chartInstances.strengthChart) chartInstances.strengthChart.destroy(); // deletes the existing strength chart instance
            chartInstances.strengthChart = new Chart(strengthCanvas, { // creates a new strength chart instance
                type: "line", // graph style from the Source
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

function loadStrengthExercises() { // loads the exercises for the strength chart. works by erasing an option and rebuilding.
    fetch("/exercise/list") // fetches the exercises from the Flask backend
        .then(function (response) {
            return response.json(); // converts the response to JSON
        })
        .then(function (data) {
            var select = document.getElementById("strengthExerciseSelect"); // gets the exercise select dropdown optioins
            if (!select) return; // if the exercise select dropdown is not found, return and do nothing
            var current = select.value; // gets the current exercise from the exercise select dropdown
            select.innerHTML = ""; // clears the exercise select dropdown
            var opt = document.createElement("option"); // creates a new option for the exercise select dropdown
            opt.value = ""; // sets the value of the new option to empty
            opt.text = "All exercises"; // sets the text of the new option to "All exercises"
            select.appendChild(opt); // adds the new option to the exercise select dropdown
            (data || []).forEach(function (ex) { // loops through the exercises
                var option = document.createElement("option"); // creates a new option for the exercise select dropdown
                option.value = ex.exercise_name; // sets the value of the new option to the exercise name
                option.text = ex.exercise_name; // sets the text of the new option to the exercise name
                select.appendChild(option); // adds the new option to the exercise select dropdown
            });
            if (current) select.value = current; // if there is a current exercise, set the value of the exercise select dropdown to the current exercise
            select.onchange = function () { // when the exercise select dropdown is changed
                var activeBtn = document.querySelector('.view-period-btn[data-chart="strength"].active'); // gets the active button
                var p = activeBtn ? activeBtn.dataset.period : 'weekly'; // gets the period from the active button
                loadStrengthChart(p); // reloads the strength chart with the new period
            };
        })
        .catch(function () { // in case of errors
            console.log("Could not load exercises."); // logs the error for debugging
        });
}

// 3. Calories chart: calories spent (orange), gained (green), net (pink) y axis = calories x axis = date
function loadCaloriesChart(period) { // loads the calories chart with the new period
    var caloriesCanvas = document.getElementById("caloriesChart"); // gets the calories chart canvas
    if (!caloriesCanvas) return; // if the calories chart canvas is not found, return and do nothing
    
    fetch("/analytics/calories?period=" + (period || "weekly")) // fetches the calories data from the Flask backend
        .then(function (response) {
            return response.json(); // converts the response to JSON
        })
        .then(function (data) {
            var labels = []; // creates an empty list to store the labels
            var spent = []; // creates an empty list to store the spent calories
            var gained = []; // creates an empty list to store the gained calories
            var net = []; // creates an empty list to store the net calories
            data.forEach(function (item) { // loops through the data
                labels.push(item.period); // adds the period to the labels list
                spent.push(item.spent != null ? item.spent : 0); // adds the spent calories to the spent list
                gained.push(item.gained != null ? item.gained : 0); // adds the gained calories to the gained list
                net.push(item.net != null ? item.net : 0); // adds the net calories to the net list
            });
            caloriesCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px"; // sets the minimum width of the calories chart canvas
            if (chartInstances.caloriesChart) { // if the calories chart instance exists
                chartInstances.caloriesChart.destroy(); // destroys the existing calories chart instance
            }
            chartInstances.caloriesChart = new Chart(caloriesCanvas, { // creates a new calories chart instance
                type: "line", // graph style from the Source but modified and added for multiple lines
                data: { // data for the calories chart
                    labels: labels, // labels for the x axis    
                    datasets: [ // datasets for the calories chart
                        { label: "Calories Spent (cal)", data: spent, borderColor: "rgb(255, 165, 0)", fill: false }, // spent calories
                        { label: "Calories Gained (cal)", data: gained, borderColor: "rgb(34, 139, 34)", fill: false }, // gained calories
                        { label: "Net Calories (cal)", data: net, borderColor: "rgb(255, 192, 203)", fill: false }, // net calories
                    ],
                },
                options: { // options for the calories chart
                    responsive: true, // makes the chart responsive
                    scales: { y: { beginAtZero: false } }, // y axis starts at 0
                },
            });
        })
        .catch(function () { // in case of errors
            console.log("Could not load calories data."); // logs the error for debugging
        });
}

// 4. Protein intake line chart: y axis = protein (g) x axis = date
function loadProteinChart(period) {
    var proteinCanvas = document.getElementById("proteinChart"); // gets the protein chart canvas
    if (!proteinCanvas) return; // if the protein chart canvas is not found, return and do nothing
    
    fetch("/analytics/protein?period=" + period) // fetches the protein data from the Flask backend
        .then(function (response) { // converts the response to JSON
            return response.json();
        })
        .then(function (data) { // loops through the data
            var labels = []; // creates an empty list to store the labels
            var protein = []; // creates an empty list to store the protein

            data.forEach(function (item) { // loops through the data
                labels.push(item.period); // adds the period to the labels list
                protein.push(item.protein); // adds the protein to the protein list
            });
            proteinCanvas.style.minWidth = Math.max(400, labels.length * 40) + "px"; // sets the minimum width of the protein chart canvas
            if (chartInstances.proteinChart) chartInstances.proteinChart.destroy(); // deletes the existing protein chart instance
            chartInstances.proteinChart = new Chart(proteinCanvas, { // creates a new protein chart instance
                type: "line", // graph style from the Source
                data: { // data for the protein chart
                    labels: labels,
                    datasets: [ // datasets for the protein chart
                        {
                            label: "Protein (g)",
                            data: protein,
                            borderColor: "rgb(54, 162, 235)",
                            backgroundColor: "rgba(54, 162, 235, 0.2)",
                            fill: true,
                        },
                    ],
                },
                options: { // options for the protein chart
                    responsive: true,
                    scales: {
                        y: { // y axis
                            beginAtZero: true,
                        },
                    },
                },
            });
        })
        .catch(function () { // in case of errors
            console.log("Could not load protein data."); // logs the error for debugging
        });
}

// 5. Circular progress charts for progress of goals created by the user
// Source: https://codepen.io/dianastanciu/pen/bGbwVNr
//
// edits made:
// 1. removed hardcoded HTML structure - now dynamically generates circles for each new goal added by user
// 2. changed from fixed animation values to dynamic calculation based on actual goal progress_percent:
//    - calculates circumference based on radius (64px)
//    - calculates stroke-dashoffset (the length of the line to be drawn / progress percentage) based on actual goal progress_percent from API
// 3. integrated with Flask backend: fetches goals from /analytics/goals endpoint
// 4. changed display values:
//    - Top value shows progress percentage (0-100%) instead of fixed "2758"
//    - Bottom value shows goal description (truncated to 15 chars)
// 5. removed multiple circle sizes (circle-big, circle-small) - using single size for all goals
// 6. added container generation for multiple goals (one chart per goal)
// 7. changed color scheme

// changes needed as the original template was a static demo with fixed values.needed to:
// - display multiple goals dynamically from the database
// - show actual progress percentages calculated from goal current_value vs target_value
// - integrate with the Flask analytics backend endpoints
// - make it responsive to user data rather than static examples
function initialiseGoalProgressCharts() {
    fetch("/analytics/goals") // fetches the goals data from the Flask backend
        .then(function (response) { // converts the response to JSON
            return response.json(); // converts the response to JSON
        })
        .then(function (data) {
            var container = document.getElementById("goalsCircularContainer"); // gets the container for the goal progress charts
            if (!container) return; // if the container is not found, return and do nothing
            
            container.innerHTML = ""; // clears the container
            
            if (data.length === 0) { // if there are no goals
                container.innerHTML = "<p>No goals set yet.</p>"; // displays a message if there are no goals
                return;
            }

            data.forEach(function (goal) { // loops through the goals
                var progressPercent = Math.min(Number(goal.progress_percent) || 0, 100); // calculates the progress percentage based on the goal progress_percent with a max of 100% and a min of 0%
                var circumference = 2 * Math.PI * 64; // radius 64px
                var offset = circumference - (progressPercent / 100) * circumference; // calculates the stroke-dashoffset(circle progress) based on the progress percentage
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
                `; //  creates the HTML for the goal progress chart
                
                container.innerHTML += circleHtml; // adds the HTML for the goal progress chart to the container
            });
        })
        .catch(function () { // in case of errors
            console.log("Could not load goals data."); // logs the error for debugging
        });
}
