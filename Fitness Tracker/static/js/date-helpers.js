// Helper functions for date inputs
// Sets the date input to today's date

function setToday(inputId) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    
    const input = document.getElementById(inputId);
    if (input) {
        input.value = dateStr;
    }
}

// Date validation: years between 1900 and 2200
function validateDate(dateInput) {
    if (!dateInput.value) {
        return false;
    }
    
    const date = new Date(dateInput.value);
    const year = date.getFullYear();
    
    if (year < 1900 || year > 2200) {
        dateInput.setCustomValidity('Year must be between 1900 and 2200');
        return false;
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
        dateInput.setCustomValidity('Please enter a valid date');
        return false;
    }
    
    dateInput.setCustomValidity('');
    return true;
}

// Add validation to all date inputs on page load
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.setAttribute('min', '1900-01-01');
        input.setAttribute('max', '2200-12-31');
        input.addEventListener('change', function() {
            validateDate(this);
        });
    });
});
