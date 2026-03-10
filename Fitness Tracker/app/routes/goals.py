# routes for goals (create, edit, update progress, delete and get progress as JSON)

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify

from ..models.goal import Goal

# blueprint for goal-related pages and API endpoints
# server side scripting -the request object to get what the user sent (form data) and response like redirect and render_template; sending them to the right page or showing a template
goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/goals", methods=["GET", "POST"]) # route for goals page
def goals_page(): # function to show all goals (GET) or create a new goal (POST)
    """
    shows all goals and allows the user to create a new one.

    1. If the request is GET, loads goals from the database and renders the goals template
    2. If the request is POST, reads the form data, creates a Goal and saves it to the database
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    if request.method == "POST": # if the request is POST, the user has submitted the create form
        goalType = request.form.get("goalType") # gets the goal type from the form
        targetValue = float(request.form.get("targetValue") or 0) # gets the target value from the form
        targetDate = request.form.get("targetDate") # gets the target date from the form
        unit = request.form.get("unit") # gets the unit from the form
        description = request.form.get("description") # gets the description from the form

        newGoal = Goal(goalType, targetValue, targetDate, unit, description) # creates a new Goal object
        newGoal.saveToDB(session["userId"]) # saves the goal to the database
        flash("Goal created.", "success") # displays success message to the user
        return redirect(url_for("goals.goals_page")) # redirects the user to the goals page

    goalList = Goal.loadGoals(session["userId"]) # loads all goals for the user from the database
    return render_template("goals.html", goals=goalList) # renders the goals template with the goal list


@goals_bp.route("/goals/edit/<int:goal_id>", methods=["POST"]) # route for editing goal details
def edit_goal(goal_id): # function to update goal description, target value, target date and unit
    """
    edits goal details (desc, targetValue, targetDate, unit). separate from updating progress (currentValue).
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    newDesc = request.form.get("desc") # gets the new description from the form
    newTargetValue = float(request.form.get("targetValue") or 0) # gets the new target value from the form
    newTargetDate = request.form.get("targetDate") # gets the new target date from the form
    newUnit = request.form.get("unit") # gets the new unit from the form

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("SELECT * FROM goals WHERE id = ? AND userId = ?;", (goal_id, session["userId"])) # executes SQL query to get the goal
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Goal not found.", "error") # displays error message to the user
        return redirect(url_for("goals.goals_page")) # redirects the user to the goals page

    goalObj = Goal(
        row["goalType"],
        newTargetValue,
        newTargetDate,
        newUnit,
        newDesc,
        goalID=row["id"],
        currentValue=row["currentValue"],
    ) # creates a Goal object with updated fields
    goalObj.saveToDB(session["userId"]) # saves the goal to the database
    flash("Goal updated.", "success") # displays success message to the user
    return redirect(url_for("goals.goals_page")) # redirects the user to the goals page


@goals_bp.route("/goals/update/<int:goal_id>", methods=["POST"]) # route for updating goal progress (current value)
def update_goal(goal_id): # function to update only the current value of a goal
    """
    updates the current value of a goal (progress only). e.g. when the user logs new weight or a new record.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    newValue = float(request.form.get("currentValue") or 0) # gets the new current value from the form

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("SELECT * FROM goals WHERE id = ? AND userId = ?;", (goal_id, session["userId"])) # executes SQL query to get the goal
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Goal not found.", "error") # displays error message to the user
        return redirect(url_for("goals.goals_page")) # redirects the user to the goals page

    goalObj = Goal(
        row["goalType"],
        row["targetValue"],
        row["targetDate"],
        row["unit"],
        row["description"],
        goalID=row["id"],
        currentValue=newValue,
    ) # creates a Goal object with updated current value
    goalObj.saveToDB(session["userId"]) # saves the goal to the database
    flash("Goal progress updated.", "success") # displays success message to the user
    return redirect(url_for("goals.goals_page")) # redirects the user to the goals page


@goals_bp.route("/goals/delete/<int:goal_id>", methods=["POST"]) # route for deleting a goal
def delete_goal(goal_id): # function to delete the goal from the database
    """
    deletes a goal. verifies the goal belongs to the user before deleting.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("SELECT * FROM goals WHERE id = ? AND userId = ?;", (goal_id, session["userId"])) # executes SQL query to get the goal
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Goal not found.", "error") # displays error message to the user
        return redirect(url_for("goals.goals_page")) # redirects the user to the goals page

    cursor.execute("DELETE FROM goals WHERE id = ? AND userId = ?;", (goal_id, session["userId"])) # executes SQL query to delete the goal
    db.commit() # saves the changes to the database

    flash("Goal deleted.", "success") # displays success message to the user
    return redirect(url_for("goals.goals_page")) # redirects the user to the goals page


@goals_bp.route("/goals/<int:goal_id>/progress") # route for getting goal progress as JSON
def goal_progress(goal_id): # function to return progress data for a specific goal as JSON (e.g. for charts)
    """
    returns progress data for a specific goal as JSON. can be used for charts.
    """
    if "userId" not in session: # if user is not logged in, return error
        return jsonify({"error": "Not logged in"}), 401

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("SELECT * FROM goals WHERE id = ? AND userId = ?;", (goal_id, session["userId"])) # executes SQL query to get the goal
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        return jsonify({"error": "Goal not found"}), 404

    goalObj = Goal(
        row["goalType"],
        row["targetValue"],
        row["targetDate"],
        row["unit"],
        row["description"],
        goalID=row["id"],
        currentValue=row["currentValue"],
    ) # creates a Goal object from the row

    progress = goalObj.calcProgress() # calculates the progress percentage

    return jsonify({
        "goalID": goalObj.goalID,
        "description": goalObj.desc,
        "targetValue": goalObj.targetValue,
        "currentValue": goalObj.currentValue,
        "progressPercent": progress,
        "unit": goalObj.unit,
        "isAchieved": progress >= 100
    }) # returns the progress data as JSON

