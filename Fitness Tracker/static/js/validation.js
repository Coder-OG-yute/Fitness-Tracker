// js validation helpers for password match on signup
// used together with the backend validation for user feedback.

document.addEventListener("DOMContentLoaded", function () { // on page load
    var passwordInput = document.getElementById("password"); // get the password input
    var confirmInput = document.getElementById("confirmPassword"); // get the confirm password input

    if (passwordInput && confirmInput) { // if the password and confirm password inputs exist
        confirmInput.addEventListener("input", function () { // on input event
            if (passwordInput.value !== confirmInput.value) { // if the password and confirm password do not match
                confirmInput.setCustomValidity("Passwords do not match."); // passwords do not match error message
            } else { // if the password and confirm password match
                confirmInput.setCustomValidity(""); // no error message
            }
        }); // for each password and confirm password input
    } 
});