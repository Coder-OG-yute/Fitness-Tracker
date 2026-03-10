// Basic client-side validation helpers.
// These work together with the backend validation to give quick feedback.

document.addEventListener("DOMContentLoaded", function () {
    var passwordInput = document.getElementById("password");
    var confirmInput = document.getElementById("confirmPassword");

    if (passwordInput && confirmInput) {
        confirmInput.addEventListener("input", function () {
            if (passwordInput.value !== confirmInput.value) {
                confirmInput.setCustomValidity("Passwords do not match.");
            } else {
                confirmInput.setCustomValidity("");
            }
        });
    }
});

