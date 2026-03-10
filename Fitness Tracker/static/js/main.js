// Handles dynamic form switching (cardio vs gym), exercise list by type, and preset selection for exercise log.
// Handles dynamic form switching, exercise autocomplete, and preset selection.


document.addEventListener("DOMContentLoaded", function () {
    // 1. Dynamic form switching for cardio vs gym exercises
    // Now exercise type is asked FIRST, then exercise name, then appropriate fields
    var exerciseTypeSelect = document.getElementById("exercise_type");
    var exerciseNameContainer = document.getElementById("exercise_name_container");
    var exerciseNameSelect = document.getElementById("exercise_name");
    var gymFields = document.getElementById("gym_fields");
    var cardioFields = document.getElementById("cardio_fields");

    var dateContainer = document.getElementById("date_container");
    
    if (exerciseTypeSelect) {
        function toggleFields() {
            var exerciseType = exerciseTypeSelect.value;
            
            if (exerciseType === "") {
                // No type selected yet - hide everything
                if (exerciseNameContainer) exerciseNameContainer.style.display = "none";
                if (gymFields) gymFields.style.display = "none";
                if (cardioFields) cardioFields.style.display = "none";
                if (dateContainer) dateContainer.style.display = "none";
                // Remove required attributes when fields are hidden
                if (exerciseNameSelect) exerciseNameSelect.removeAttribute("required");
                var dateInput = document.getElementById("date");
                if (dateInput) dateInput.removeAttribute("required");
                var weightInput = document.getElementById("weight");
                var setsInput = document.getElementById("sets");
                var repsInput = document.getElementById("reps");
                var durationInput = document.getElementById("duration");
                if (weightInput) weightInput.removeAttribute("required");
                if (setsInput) setsInput.removeAttribute("required");
                if (repsInput) repsInput.removeAttribute("required");
                if (durationInput) durationInput.removeAttribute("required");
            } else {
                // Type selected - show exercise name selection and date
                if (exerciseNameContainer) exerciseNameContainer.style.display = "block";
                if (dateContainer) dateContainer.style.display = "block";
                
                // Set required attributes when fields are shown
                if (exerciseNameSelect) exerciseNameSelect.setAttribute("required", "required");
                if (dateContainer) {
                    var dateInput = document.getElementById("date");
                    if (dateInput) dateInput.setAttribute("required", "required");
                }
                
                // Filter exercises by type
                if (exerciseNameSelect) {
                    exerciseNameSelect.innerHTML = '<option value="">-- Choose an exercise --</option>';
                    fetch('/exercise/list?type=' + exerciseType)
                        .then(response => response.json())
                        .then(data => {
                            data.forEach(function(exercise) {
                                var option = document.createElement('option');
                                option.value = exercise.exercise_name;
                                option.text = exercise.exercise_name;
                                exerciseNameSelect.appendChild(option);
                            });
                        })
                        .catch(function() {
                            console.log('Could not load exercises.');
                        });
                }
                
                if (exerciseType === "cardio") {
                    // For cardio, show duration only
                    if (gymFields) gymFields.style.display = "none";
                    if (cardioFields) cardioFields.style.display = "block";
                    // Set required for cardio fields
                    var durationInput = document.getElementById("duration");
                    if (durationInput) durationInput.setAttribute("required", "required");
                    // Remove required from gym fields
                    var weightInput = document.getElementById("weight");
                    var setsInput = document.getElementById("sets");
                    var repsInput = document.getElementById("reps");
                    if (weightInput) weightInput.removeAttribute("required");
                    if (setsInput) setsInput.removeAttribute("required");
                    if (repsInput) repsInput.removeAttribute("required");
                } else if (exerciseType === "gym") {
                    // For gym, show weight, sets and reps
                    if (gymFields) gymFields.style.display = "block";
                    if (cardioFields) cardioFields.style.display = "none";
                    // Set required for gym fields
                    var weightInput = document.getElementById("weight");
                    var setsInput = document.getElementById("sets");
                    var repsInput = document.getElementById("reps");
                    if (weightInput) weightInput.setAttribute("required", "required");
                    if (setsInput) setsInput.setAttribute("required", "required");
                    if (repsInput) repsInput.setAttribute("required", "required");
                    // Remove required from cardio fields
                    var durationInput = document.getElementById("duration");
                    if (durationInput) durationInput.removeAttribute("required");
                }
            }
        }

        // Set initial state
        toggleFields();

        // Update when selection changes
        exerciseTypeSelect.addEventListener("change", toggleFields);
    }

    // 2. Exercise search/autocomplete
    var exerciseNameSelect = document.getElementById("exercise_name");
    var exerciseSearchInput = null;

    // If there's a select box, we can add a search input above it
    if (exerciseNameSelect) {
        // Create a search input field
        var searchDiv = document.createElement("div");
        searchDiv.innerHTML = '<input type="text" id="exercise_search" placeholder="Search exercises...">';
        exerciseNameSelect.parentNode.insertBefore(searchDiv, exerciseNameSelect);
        exerciseSearchInput = document.getElementById("exercise_search");

        if (exerciseSearchInput) {
            exerciseSearchInput.addEventListener("input", function() {
                var searchTerm = this.value.toLowerCase();
                var options = exerciseNameSelect.options;

                for (var i = 0; i < options.length; i++) {
                    var optionText = options[i].text.toLowerCase();
                    if (optionText.includes(searchTerm) || searchTerm === "") {
                        options[i].style.display = "";
                    } else {
                        options[i].style.display = "none";
                    }
                }
            });
        }
    }

    // 3. Workout selection dropdown (if on exercise log page)
    var workoutSelect = document.getElementById("workout_select");
    if (workoutSelect) {
        // Load workouts
        fetch("/exercise/presets")
            .then(response => response.json())
            .then(data => {
                data.forEach(function(workout) {
                    var option = document.createElement("option");
                    option.value = workout.id;
                    option.text = workout.preset_name;
                    workoutSelect.appendChild(option);
                });
            })
            .catch(function() {
                console.log("Could not load workouts.");
            });
        
        workoutSelect.addEventListener("change", function() {
            var workoutId = this.value;
            if (workoutId) {
                window.location.href = "/exercise/preset/use/" + workoutId;
            }
        });
    }

    // 4. Random tip functionality (for tips page)
    var tipButton = document.getElementById("tipButton");
    var tipBox = document.getElementById("tipBox");

    if (tipButton && tipBox) {
        tipButton.addEventListener("click", function () {
            // Call the /tips/random endpoint to get a JSON tip.
            fetch("/tips/random")
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    // Show the tip title and content in the box.
                    tipBox.innerHTML =
                        "<h2>" +
                        data.title +
                        "</h2><p>" +
                        data.content +
                        "</p><p><em>" +
                        data.source +
                        "</em></p>";
                })
                .catch(function () {
                    tipBox.innerHTML = "<p>Could not load a tip right now.</p>";
                });
        });
    }
});


