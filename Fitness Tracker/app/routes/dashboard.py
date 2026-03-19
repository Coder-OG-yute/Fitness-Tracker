from flask import Blueprint, render_template, session, redirect, url_for, request, flash, g, jsonify
from ..utils.db import currentTime


# importing blueprint for organised routes handling the dashboard page and its routes
# render_template for rendering templates on the page
# session for storing session data, like userId, username
# redirect for redirecting to a different page, like login.html
# url_for for generating URLs
# request for handling requests, GET, POST, PUT, DELETE, etc.
# flash for displaying messages, like success, error
# g for accessing the database
# currentTime for getting the current time, using utils.db to get the current time and format it as a string
# server side scripting -the request object to get what the user sent (form data) and response like redirect and render_template; sending them to the right page or showing a template
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    """
    dashboard/home page that shows a welcome message and links to other pages   

    """
    # If the user is not logged in, send them to the login page.
    if "userId" not in session: # if the user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    username = session.get("username") # get the username from the session
    return render_template("dashboard.html", username=username) # render the dashboard template with the username


@dashboard_bp.route("/calendar") # route for main calendar page
def calendar(): # function to render the calendar page with diet and exercise log toggle
    """
    main calendar and history page with toggle between Diet and Exercise logs.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    return render_template("calendar.html", view_mode="month") # render the calendar template with default month view


@dashboard_bp.route("/calendar/logs") # route for calendar logs as JSON
def calendar_logs(): # function to return exercise or diet logs for the calendar view as JSON
    """
    returns exercise or diet logs for the calendar view as JSON.
    used by the calendar page to display logs in the calendar cells.
    """
    if "userId" not in session: # if user is not logged in, return error
        return jsonify({"error": "Not logged in"}), 401# returns error message as JSON and 401 status code

    log_type = request.args.get("type", "exercise") # gets the log type from the request (exercise or diet). uses server-side scripting using request and response objects
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    if log_type == "exercise": # if log type is exercise, executes following SQL query
        cursor.execute(
            """
            SELECT el.logId, el.date, e.exerciseName, el.sets, el.reps, el.duration, el.caloriesBurned, el.weight
            FROM exerciseLogs el
            JOIN exercises e ON el.exerciseId = e.exerciseId
            WHERE el.userId = ?
            ORDER BY el.date DESC;
            """,
            (session["userId"],)
        ) # executes SQL query to get exercise logs for the user. uses cross-table parameterised SQL
        rows = cursor.fetchall() # fetches all rows from the database
        logs = [] # creates an empty list to store the logs
        for row in rows: # loops through the rows
            logs.append({
                "logId": row["logId"],
                "date": row["date"],
                "exerciseName": row["exerciseName"],
                "sets": row["sets"],
                "reps": row["reps"],
                "duration": row["duration"],
                "weight": row["weight"],
                "caloriesBurned": row["caloriesBurned"],
                "workoutName": None
            }) # appends each exercise log to the list
    else: # if log type is diet, executes following SQL query
        cursor.execute(
            """
            SELECT logId, date, foodName, mass, calories, protein
            FROM dietLogs
            WHERE userId = ?
            ORDER BY date DESC;
            """,
            (session["userId"],)
        ) # executes SQL query to get diet logs for the user
        rows = cursor.fetchall() # fetches all rows from the database
        logs = [] # creates an empty list to store the logs
        for row in rows: # loops through the rows
            logs.append({
                "logId": row["logId"],
                "date": row["date"],
                "foodName": row["foodName"],
                "mass": row["mass"],
                "calories": row["calories"],
                "protein": row["protein"]
            }) # appends each diet log to the list

    return jsonify(logs) # returns the logs as JSON


def renderWeightLog(): 
    """
    helper function to render the weight log page with entries and paging
    used for GET request or when re-rendering after a validation error.
    """
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT id, date, weight FROM bodyWeight WHERE userId = ? ORDER BY date DESC;",
        (session["userId"],)
    ) # executes SQL query to get weight entries for the user
    rows = cursor.fetchall() # fetches all rows from the database
    all_entries = [{"id": row["id"], "date": row["date"], "weight": row["weight"]} for row in rows] # creates a list of weight entries
    per_page = 10 # sets the number of entries per page
    page = request.args.get("page", 1, type=int) # gets the current page from the request
    page = max(1, page) # ensures page is at least 1
    start = (page - 1) * per_page # calculates the start index for the current page
    end = start + per_page # calculates the end index for the current page
    weightEntries = all_entries[start:end] # gets the weight entries for the current page
    total_pages = (len(all_entries) + per_page - 1) // per_page if all_entries else 1 # calculates the total number of pages
    return render_template(
        "weight_log.html",
        weightEntries=weightEntries,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
    ) # renders the weight log template with the entries and pages


@dashboard_bp.route("/weight/log", methods=["GET", "POST"]) # route for logging body weight
def log_weight(): # function to display weight log (GET) or save a weight entry (POST)
    """
    allows users to log their body weight.

    1. If the request is GET, shows the weight log form with history and paging
    2. If the request is POST, validates weight and date then saves the entry to the database
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    if request.method == "POST": # if the request is POST, the user has submitted the form
        weightInp = request.form.get("weight") # gets the weight from the form
        dateInp = request.form.get("date") # gets the date from the form

        # 1) validate that weight is a positive number
        try:
            weightValue = float(weightInp) # converts the weight to a float
            if weightValue <= 0: # if the weight is not a positive number, display error message
                flash("Weight must be a positive number.", "error")
                return renderWeightLog() # renders the weight log template with the entries and pages
        except (ValueError, TypeError): # if the weight is not a valid number, display error message
            flash("Please enter a valid weight number.", "error")
            return renderWeightLog() # renders the weight log template with the entries and pages

        # 2) validate date and that year is between 1900 and 2200
        if dateInp: # if the date is provided, validate it
            try:
                from datetime import datetime # imports the datetime module
                dateObj = datetime.strptime(dateInp, "%Y-%m-%d") # converts the date to a datetime object
                year = dateObj.year # gets the year from the datetime object
                if year < 1900 or year > 2200: # if the year is not between 1900 and 2200, display error message
                    flash("Year must be between 1900 and 2200.", "error")
                    return renderWeightLog() # renders the weight log template with the entries and pages
            except ValueError: # if the date is not a valid date, display error message
                flash("Please enter a valid date.", "error")
                return renderWeightLog() # renders the weight log template with the entries and pages
        else: # if the date is not provided, use the current date
            dateInp = currentTime().split()[0] # uses current date if none provided (date part only)

        db = g.db # gets the database connection
        cursor = db.cursor() # gets the database cursor

        # 3) save the weight entry to the database
        createdAt = currentTime() # gets the current time for the createdAt field
        cursor.execute(
            "INSERT INTO bodyWeight (userId, weight, date, createdAt) VALUES (?, ?, ?, ?);",
            (session["userId"], weightValue, dateInp, createdAt)
        ) # executes SQL query to insert the weight entry
        db.commit() # saves the changes to the database

        flash(f"Weight of {weightValue} kg logged successfully for {dateInp}.", "success") # displays success message to the user
        return redirect(url_for("dashboard.home")) # redirects the user to the dashboard

    # if the request is GET, show the form and weight history with pagination
    return renderWeightLog()


@dashboard_bp.route("/weight/edit/<int:entry_id>", methods=["GET", "POST"]) # route for editing a weight entry
def edit_weight(entry_id): # function to show edit form (GET) or update the weight entry (POST)
    """
    edits a single weight entry.

    1. If the request is GET, shows the edit form with the current entry values
    2. If the request is POST, validates the input and updates the entry in the database
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT id, date, weight FROM bodyWeight WHERE userId = ? AND id = ?;",
        (session["userId"], entry_id)
    ) # executes SQL query to get the weight entry for the user
    row = cursor.fetchone() # fetches the result from the query
    if not row:
        flash("Weight entry not found.", "error") # displays error message to the user
        return redirect(url_for("dashboard.log_weight")) # redirects the user to the weight log page
    if request.method == "POST": # if the request is POST, the user has submitted the edit form
        weightInp = request.form.get("weight") # gets the weight from the form
        dateInp = request.form.get("date") # gets the date from the form
        try:
            weightValue = float(weightInp) # converts the weight to a float
            if weightValue <= 0: # if the weight is not a positive number, display error message
                flash("Weight must be a positive number.", "error")
                return renderWeightLog() # renders the weight log template with the entries and pages
        except (ValueError, TypeError): # if the weight is not a valid number, display error message
            flash("Please enter a valid weight number.", "error")
            return renderWeightLog() # renders the weight log template with the entries and pages
        if dateInp: # if the date is provided, validate it
            try:
                from datetime import datetime # imports the datetime module
                dateObj = datetime.strptime(dateInp, "%Y-%m-%d") # converts the date to a datetime object
                year = dateObj.year # gets the year from the datetime object
                if year < 1900 or year > 2200: # if the year is not between 1900 and 2200, display error message
                    flash("Year must be between 1900 and 2200.", "error")
                    return renderWeightLog() # renders the weight log template with the entries and pages
            except ValueError: # if the date is not a valid date, display error message
                flash("Please enter a valid date.", "error")
                return renderWeightLog() # renders the weight log template with the entries and pages
        else: # if the date is not provided, use the existing date
            dateInp = row["date"] # keeps the existing date if none provided
        cursor.execute(
            "UPDATE bodyWeight SET weight = ?, date = ? WHERE id = ? AND userId = ?;",
            (weightValue, dateInp, entry_id, session["userId"])
        ) # executes SQL query to update the weight entry
        db.commit() # saves the changes to the database
        flash("Weight entry updated.", "success") # displays success message to the user
        return redirect(url_for("dashboard.log_weight")) # redirects the user to the weight log page
    # if the request is GET, show the form with this entry for editing
    entry = {"id": row["id"], "date": row["date"], "weight": row["weight"]} # builds the entry dict for the template
    return render_template("weight_log.html", weightEntries=[], page=1, total_pages=1, per_page=10, edit_entry=entry) # renders the weight log template with the entry to edit


@dashboard_bp.route("/weight/delete/<int:entry_id>", methods=["POST"]) # route for deleting a weight entry
def delete_weight(entry_id): # function to delete a single weight entry
    """
    deletes a single weight entry from the database.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "DELETE FROM bodyWeight WHERE id = ? AND userId = ?;",
        (entry_id, session["userId"])
    ) # executes SQL query to delete the weight entry
    db.commit() # saves the changes to the database
    if cursor.rowcount: # if the weight entry was deleted, display success message
        flash("Weight entry deleted.", "success") # displays success message to the user
    else: # if the weight entry was not deleted, display error message 
        flash("Weight entry not found.", "error") # displays error message to the user
    return redirect(url_for("dashboard.log_weight")) # redirects the user to the weight log page


@dashboard_bp.route("/weight/history") # route for weight history as JSON
def weight_history(): # function to return weight history data as JSON for charts
    """
    returns weight history as JSON for charts.
    used by the analytics page 
    """
    if "userId" not in session: # if user is not logged in, return error
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT date, weight FROM bodyWeight WHERE userId = ? ORDER BY date ASC;",
        (session["userId"],)
    ) # executes SQL query to get weight history for the user
    rows = cursor.fetchall() # fetches all rows from the database
    dataList = [] # creates an empty list to store the data
    for row in rows: # loops through the rows
        dataList.append({"date": row["date"], "weight": row["weight"]}) # appends each weight entry to the list
    return jsonify(dataList) # returns the data as JSON

