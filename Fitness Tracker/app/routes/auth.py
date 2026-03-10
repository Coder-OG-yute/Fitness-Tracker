from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g

from ..utils.db import currentTime
from ..utils.password import valPass


# importing blueprint for organised routes
# render_template for rendering templates on the page
# request for handling requests, GET, POST, PUT, DELETE, etc.
# redirect for redirecting to a different page, like login.html
# url_for for generating URLs
# session for storing session data, like userId, username
# flash for displaying messages, like success, error
# g for accessing the database
# generate_password_hash for hashing passwords, using werkzeug.security to hash the password, 
# ensuring user security so if passowrds intercepted, it is encrypted and cant be read as plain text using the pbkdf2:sha256 method.
# check_password_hash for checking passwords are an existing stored hash in the database, using werkzeug.security
# currentTime for getting the current time, using utils.db to get the current time and format it as a string
# valPass for validating passwords, function i created in utils.password to validate the password strength
# server side scripting -the request object to get what the user sent (form data) and response like redirect and render_template; sending them to the right page or showing a template
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    handles user sign-up (registration)

    Algorithm of log in process:
    1. If the request is GET, show the empty sign-up form
    2. If the request is POST:
       - Reads the username, email, password and confirmPassword from the request form
       - Checks that both passwords are the same
       - Validates the password strength using our helper function valPass
       - Checks that the username or email is not already used
       - Hashes the password using generate_password_hash with method='pbkdf2:sha256'
       - Inserts the new user into the database with the current time
       - Redirects the user to the login page if successful and displays a success message
"""
    if request.method == "POST": # if the request is POST, then the user has submitted the form (registration)
        username = request.form.get("username")# gets the username from the registration
        email = request.form.get("email")# gets the email from the registration
        password = request.form.get("password")# gets the password from the registration
        confirmPassword = request.form.get("confirmPassword")# gets the confirm password from the registration

        # 1) Check if the two password fields match.
        if password != confirmPassword:
            flash("Passwords do not match. Please try again.", "error") # displays error message to the user if the 2 passwords dont match
            return render_template("signup.html") # renders the signup template to the user

        # 2) Validate the password using which i set to be (length min 8, upper case, lower case, digit, symbol present).
        isValid, errorList = valPass(password) # validates the password strength using function i created  from utils.password.py 
        #and gives boolean is it valid or not and a list of error messages if present
        if not isValid: #if isValid is false
            # put all error messages into one line so the user knows what to fix
            flash(" ".join(errorList), "error") # displays error message to the user if the password is not valid
            return render_template("signup.html") # renders the signup template to the user to signup again

        # 3) Make sure the username or email is not already in the database.
        db = g.db # gets the database from the global context
        cursor = db.cursor() # gets the cursor from the database
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?;", (username, email)) # executes the query to check if the username or email is already in the database
        existingUser = cursor.fetchone() # fetches the result from the query
        if existingUser is not None: # if the username or email is already in the database
            flash("Username or email already exists. Please choose something else.", "error") # displays error message to the user if the username or email is already in the database
            return render_template("signup.html") # renders the signup template to the user to signup again

        # 4) Hash the valid password using pbkdf2:sha256 (Werkzeug's supported method).
        passwordHash = generate_password_hash(password, method="pbkdf2:sha256") # uses hashing

        # 5) Save the new user in the database with the current time.
        createdAt = currentTime() # gets the current time and formats it as a string
        cursor.execute(
            "INSERT INTO users (username, email, passwordHash, createdAt) VALUES (?, ?, ?, ?);",
            (username, email, passwordHash, createdAt),
        )
        db.commit() # adds the new user and details to the database

        flash("Account created successfully! You can now log in.", "success")# displays success message to the user if the account is created successfully
        return redirect(url_for("auth.login"))# redirects the user to the login page

    # If the request is GET, just show the registration form
    return render_template("signup.html") # renders the signup template to the user to signup


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    handles user login.

    Algorithm of log in process:
    1. If the request is GET, show the login form
    2. If the request is POST:
       - Reads the username and password from the request form
       - Looks up the user in the database by username
       - If the user exists, compares the entered password with the stored hash using check_password_hash
       - If it matches, stores userId and username in the session and redirects the user to the dashboard
       - Otherwise, shows an error message
    """
    if request.method == "POST": # if the request is POST, then the user has submitted the login form
        username = request.form.get("username")# gets the username from the login form
        password = request.form.get("password")# gets the password from the login form

        db = g.db
        cursor = db.cursor()

        # 1) find the user by username
        cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))# executes the query to find the user in the database by username
        userRow = cursor.fetchone()# fetches the result from the query

        if userRow is None:
            # No user found with this username.
            flash("Invalid username or password.", "error")# displays error message to the user if the username or password is incorrect
            return render_template("login.html")# renders the login template to the user to login again

        storedHash = userRow["passwordHash"]# gets the stored hash from the user row

        # 2) compares the entered password with the stored hash
        isValid = check_password_hash(storedHash, password)# compares the entered password with the stored hash using check_password_hash

        if not isValid: #if isValid is false
            flash("Invalid username or password.", "error")# displays error message to the user if the username or password is incorrect
            return render_template("login.html")# renders the login template to the user to login again

        # 3) Save basic user info in the session so we know who is logged in.
        session["userId"] = userRow["userId"]# stores the user id in the session
        session["username"] = userRow["username"]# stores the username in the session

        flash("Logged in successfully.", "success")# displays success message to the user if the login is successful
        return redirect(url_for("dashboard.home"))# redirects the user to the dashboard

    # For GET requests, just show the login form.
    return render_template("login.html")# renders the login template to the user to login


@auth_bp.route("/logout")
def logout():
    """
    logs the user out

    1. Clears the session so no user is stored
    2. Displays a message
    3. Redirects the user to the login page
    """
    session.clear()# clears the session so no user is stored
    flash("You have been logged out.", "info")# displays info message to the user if the logout is successful
    return redirect(url_for("auth.login"))# redirects the user to the login page
