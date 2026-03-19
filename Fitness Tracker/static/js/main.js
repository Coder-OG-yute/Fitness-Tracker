//exercise log form (gym/cardio required options in drop down toggled by exercise type (duration for cardio not gym and sets for gym not cardio),
// exercise search and autocomplete, workout preset dropdown, tips page random tip.



document.addEventListener("DOMContentLoaded", function () {
    // 1. Exercise type (gym/cardio) and name dropdown
        //  exercise type is asked first, then exercise name, so appropriate fields in drop down are showed and mitigate errors 
        // which was being faced, but user who tested, reccomended this chang

    var exerciseTypeSelect = document.getElementById("exercise_type"); // type select
    var exerciseNameContainer = document.getElementById("exercise_name_container"); // container for exercise name select
    var exerciseNameSelect = document.getElementById("exercise_name"); // exercise name select
    var gymFields = document.getElementById("gym_fields"); // weight, sets, reps
    var cardioFields = document.getElementById("cardio_fields"); // duration
    var dateContainer = document.getElementById("date_container"); // date input area

    if (exerciseTypeSelect) {
        function toggleFields() {
            var exerciseType = exerciseTypeSelect.value; // current type (gym, cardio, or empty)

            if (exerciseType === "") {
                // if no type is selected: hide all type-specific UI and clear required
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
                
                // filter exercise options by type
                if (exerciseNameSelect) {
                    var allOptions = exerciseNameSelect.querySelectorAll('option[data-type]');
                    exerciseNameSelect.innerHTML = '<option value="">-- Choose an exercise --</option>';
                    allOptions.forEach(function(opt) {
                        if (opt.getAttribute('data-type') === exerciseType) {
                            var clone = opt.cloneNode(true);
                            exerciseNameSelect.appendChild(clone);
                        }
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
        toggleFields(); // set initial visibility
        exerciseTypeSelect.addEventListener("change", toggleFields); // makes the toggleFields function run when the exercise type is changed
    }

    // 2. Exercise search/autocomplete
    var exerciseNameSelect = document.getElementById("exercise_name");
    var exerciseSearchInput = null;

    // if exercise name select is found, create a search input above it
    if (exerciseNameSelect) {
        // create a search input field
        var searchDiv = document.createElement("div");
        searchDiv.innerHTML = '<input type="text" id="exercise_search" placeholder="Search exercises...">';
        exerciseNameSelect.parentNode.insertBefore(searchDiv, exerciseNameSelect); // insert the search input field above the exercise name select
        exerciseSearchInput = document.getElementById("exercise_search"); // get the search input field

        if (exerciseSearchInput) { // if the search input field is found 
            exerciseSearchInput.addEventListener("input", function() { // add an event listener to it to run the function when the input is changed
                var searchTerm = this.value.toLowerCase(); // get the search term
                var options = exerciseNameSelect.options; // get the options

                for (var i = 0; i < options.length; i++) { // loop through the options
                    var optionText = options[i].text.toLowerCase(); // get the text of the option
                    if (optionText.includes(searchTerm) || searchTerm === "") { // if the text of the option includes the search term or the search term is empty
                        options[i].style.display = ""; // show the option
                    } else { // if the text of the option does not include the search term
                        options[i].style.display = "none"; // hide the option
                    }
                }
            });
        }
    }

    //3. Workout preset dropdown: load presets, navigate to use preset 
    var workoutSelect = document.getElementById("workout_select"); // get the workout select
    if (workoutSelect) {
        // Load workouts
        fetch("/exercise/presets")
            .then(response => response.json()) // convert the response to JSON
            .then(data => { // loop through the workouts
                data.forEach(function(workout) { 
                    var option = document.createElement("option"); // create a new option for the workout select
                    option.value = workout.id; // set the value of the new option to the workout id
                    option.text = workout.presetName || workout.preset_name || 'Workout'; // set the text of the new option to the workout name
                    workoutSelect.appendChild(option);
                }); // append the new option to the workout select
            })
            .catch(function() { // in case of errors
                console.log("Could not load workouts."); // log the error for debugging
            });
        
        workoutSelect.addEventListener("change", function() { // add an event listener to the workout select to run the function when the value is changed
            var workoutId = this.value; // get the value of the workout select
            if (workoutId) { // if the workout id is not empty
                window.location.href = "/exercise/preset/use/" + workoutId; // redirect to the use preset page
            }
        });
    }

    // 4.  give random tip button for tips page from the database
    var tipButton = document.getElementById("tipButton"); // get the tip button
    var tipBox = document.getElementById("tipBox"); // get the tip box

    if (tipButton && tipBox) { // if the tip button and tip box are found
        tipButton.addEventListener("click", function () { // add an event listener to the tip button to run the function when the button is clicked
            // call the /tips/random endpoint to get a JSON tip.
            fetch("/tips/random") // fetch the random tip from the database
                .then(function (response) {
                    return response.json(); // convert the response to JSON
                })
                .then(function (data) { // loop through the tips
                    // Show the tip title and content in the box.
                    tipBox.innerHTML = // set the inner HTML of the tip box to the tip title and content
                        "<h2>" + 
                        data.title + // add the tip title to the tip box
                        "</h2><p>" + 
                        data.content + // add the tip content to the tip box
                        "</p><p><em>" +
                        data.source + // add the tip source to the tip box
                        "</em></p>";
                })
                .catch(function () { // in case of errors
                    tipBox.innerHTML = "<p>Could not load a tip right now.</p>"; // set the inner HTML of the tip box to the error message
                });
        });
    }
});


