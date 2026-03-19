// Helper functions for date inputs


// todays date button that sets the date input to todays date
function setToday(inputId) {
    const today = new Date(); // get todays date
    const year = today.getFullYear(); // get year
    const month = String(today.getMonth() + 1).padStart(2, '0'); // get month
    const day = String(today.getDate()).padStart(2, '0'); // get day
    const dateStr = `${year}-${month}-${day}`; // format date as YYYY-MM-DD
    
    const input = document.getElementById(inputId); // get the date input
    if (input) { // if the date input exists
        input.value = dateStr; // set the date input to todays date
    }
}

// date validation (year between 1900 and 2200)
function validateDate(dateInput) {
    if (!dateInput.value) { // if the date input is empty, return false
        return false;
    }
    
    const date = new Date(dateInput.value); // get the date
    const year = date.getFullYear(); // get the year
    
    if (year < 1900 || year > 2200) { // if the year is not between 1900 and 2200, return false
        dateInput.setCustomValidity('Year must be between 1900 and 2200'); // this function allows user to see error message
        return false;
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) { // if the date is not a valid date, return false
        dateInput.setCustomValidity('Please enter a valid date'); // this function allows user to see error message
        return false;
    }
    
    dateInput.setCustomValidity(''); // no error message
    return true;
}

// Add validation to all date inputs on page load
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]'); // get all date inputs
    dateInputs.forEach(input => {
        input.setAttribute('min', '1900-01-01'); // set the minimum date to 1900-01-01
        input.setAttribute('max', '2200-12-31'); // set the maximum date to 2200-12-31
        input.addEventListener('change', function() {
            validateDate(this); // validate the date
        });
    }); // for each date input, set the minimum and maximum dates
});
