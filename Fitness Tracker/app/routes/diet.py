# routes for diet and food logging (log food, search, edit and delete diet entries)

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify

from ..utils.nutrition import calcNutrients
from ..utils.fatsecret_api import getFoodMacro


# Blueprint for diet and food logging.
diet_bp = Blueprint("diet", __name__)


@diet_bp.route("/diet/log", methods=["GET", "POST"]) # route for logging a food item
def dietLog(): # function to show diet log form (GET) or save a food entry (POST)
    """
    handles logging a food item with its mass in grams:

    1. If the request is GET, shows empty diet log form
    2. If the request is POST:
       - reads the food name, mass and date from the form
       - converts mass to a float and validates it
       - calls the nutrition helper (FatSecret API) to get calories and protein
       - validates the date and saves the entry into the dietLogs table
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    if request.method == "POST": # if the request is POST, the user has submitted the form
        foodInp = request.form.get("foodName") # gets the food name from the form
        massStr = request.form.get("mass") # gets the mass in grams from the form
        dateVal = request.form.get("date") # gets the date from the form

        # 1) convert the mass input to a float (grams)
        try:
            mass = float(massStr)
        except (TypeError, ValueError):# if the mass is not a valid number
            flash("Please enter a valid number for mass in grams.", "error") # displays error message to the user
            return render_template("dietLog.html") # renders the diet log template

        # 2) use the nutrition helper from FatSecret to get calories and protein
        result = calcNutrients(foodInp, mass)
        if result is None: # if no results are found
            flash("No results found for that food. Please try a different name.", "error") # displays error message to the user
            return render_template("dietLog.html") # renders the diet log template

        foodName = result["foodName"] # gets the food name from the result
        calories = result["calories"] # gets the calories from the result
        protein = result["protein"] # gets the protein from the result

        # 3) validate date (year between 1900 and 2200)
        if not dateVal or dateVal.strip() == "": # if the dateVal is false or is empty (.strip used to remove whitespace from the beginning and end of the string)
            flash("Please enter a date.", "error") # displays error message to the user
            return render_template("dietLog.html")# renders the diet log template
        try: # try to convert the date to a datetime object
            import datetime
            dateObj = datetime.datetime.strptime(dateVal, "%Y-%m-%d") # converts the date to a datetime object
            if dateObj.year < 1900 or dateObj.year > 2200: # if the year is not between 1900 and 2200
                flash("Year must be between 1900 and 2200.", "error") # displays error message to the user
                return render_template("dietLog.html") # renders the diet log template
        except ValueError: # if the date is not a valid date
            flash("Please enter a valid date.", "error") # displays error message to the user
            return render_template("dietLog.html") # renders the diet log template

        db = g.db # gets the database connection
        cursor = db.cursor() # gets the database cursor
        cursor.execute(
            """
            INSERT INTO dietLogs (userId, foodName, date, mass, calories, protein)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (session["userId"], foodName, dateVal, mass, calories, protein),
        ) # executes SQL query to insert the diet log entry
        db.commit() # saves the changes to the database

        flash(f"Logged {foodName}: {protein} g protein, {calories} cal.", "success") # displays success message to the user
        return redirect(url_for("dashboard.home")) # redirects the user to the dashboard

    # if the request is GET, show the empty form
    return render_template("dietLog.html") # renders the diet log template



@diet_bp.route("/diet/log/edit/<int:log_id>", methods=["GET", "POST"]) # route for editing a diet log entry
def edit_diet_log(log_id): # function to show edit form (GET) or update the entry (POST)
    """
    edits a diet log entry. GET shows the form with current data; POST updates the entry in the database.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT logId, date, foodName, mass, calories, protein FROM dietLogs WHERE logId = ? AND userId = ?;",
        (log_id, session["userId"])
    ) # executes SQL query to get the diet log entry
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Diet log not found.", "error") # displays error message to the user
        return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar

    if request.method == "GET": # if the request is GET, show the edit form
        return render_template("diet_log_edit.html", log=dict(row), log_id=log_id) # renders the edit template with the log data

    foodName = request.form.get("foodName") # gets the food name from the form
    mass = float(request.form.get("mass") or 0) # gets the mass from the form
    dateVal = request.form.get("date") # gets the date from the form

    from ..utils.fatsecret_api import getFoodMacro
    macros = getFoodMacro(foodName, mass) # gets calories and protein from the FatSecret API
    calories = macros["calories"] # gets the calories from the API result
    protein = macros["protein"] # gets the protein from the API result

    cursor.execute(
        """
        UPDATE dietLogs
        SET foodName = ?, mass = ?, calories = ?, protein = ?, date = ?
        WHERE logId = ? AND userId = ?;
        """,
        (foodName, mass, calories, protein, dateVal, log_id, session["userId"])
    ) # executes SQL query to update the diet log entry
    db.commit() # saves the changes to the database

    flash("Diet log updated.", "success") # displays success message to the user
    return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar


@diet_bp.route("/diet/log/delete/<int:log_id>", methods=["POST"]) # route for deleting a diet log entry
def delete_diet_log(log_id): # function to delete the diet log entry from the database
    """
    deletes a diet log entry. verifies the log belongs to the user before deleting.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("SELECT * FROM dietLogs WHERE logId = ? AND userId = ?;", (log_id, session["userId"])) # verifies the log belongs to the user
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Diet log not found.", "error") # displays error message to the user
        return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar

    cursor.execute("DELETE FROM dietLogs WHERE logId = ? AND userId = ?;", (log_id, session["userId"])) # executes SQL query to delete the entry
    db.commit() # saves the changes to the database

    flash("Diet log deleted.", "success") # displays success message to the user
    return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar


@diet_bp.route("/calendar/log/diet/<int:log_id>") # route for getting a single diet log entry as JSON
def get_diet_log(log_id): # function to return one diet log entry as JSON for the calendar or editing
    """
    returns a single diet log entry as JSON. used by the calendar or edit flow.
    """
    if "userId" not in session: # if user is not logged in, return error
        return jsonify({"error": "Not logged in"}), 401

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT logId, date, foodName, mass, calories, protein FROM dietLogs WHERE logId = ? AND userId = ?;",
        (log_id, session["userId"])
    ) # executes SQL query to get the diet log entry
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        return jsonify({"error": "Log not found"}), 404

    return jsonify({
        "logId": row["logId"],
        "date": row["date"],
        "foodName": row["foodName"],
        "mass": row["mass"],
        "calories": row["calories"],
        "protein": row["protein"]
    }) # returns the log data as JSON



