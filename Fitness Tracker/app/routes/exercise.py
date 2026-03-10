# routes for exercise logging, exercise list, presets, workouts and calendar log endpoints

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify
import datetime

from ..utils.db import currentTime
from ..utils.search import binSearch
from ..models.preset import WorkoutPreset, ExercisePreset, PresetInstance


# blueprint for all exercise related pages and API endpoints
exercise_bp = Blueprint("exercise", __name__)


def get_all_exercise_names_and_ids(): # helper to load all exercise names and ids from the database
    """
    reads all exercise names from the database and returns sorted name list and parallel id list.
    the id list is used so that after binary search on names we can get the correct exercise_id.
    """
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("SELECT exerciseId, exerciseName FROM exercises ORDER BY exerciseName ASC;") # executes SQL query to get all exercises. uses mergesort or similarly efficient sort (ORDER BY)
    rows = cursor.fetchall() # fetches all rows from the database

    nameList = [] # creates an empty list for names. uses list operations
    idList = [] # creates an empty list for ids
    for row in rows:
        nameList.append(row["exerciseName"]) # appends the exercise name to the list
        idList.append(row["exerciseId"]) # appends the exercise id to the list

    return nameList, idList # returns both lists


@exercise_bp.route("/exercise/log", methods=["GET", "POST"]) # route for logging an exercise session
def exercise_log(): # function to show exercise log form (GET) or save an exercise entry (POST)
    """
    handles logging an exercise session.

    1. If GET, loads exercise names and renders the log form
    2. If POST: reads form (exercise name, type, sets, reps, weight, duration, date), validates,
       finds exercise by binary search, gets MET from DB, calculates calories, inserts into exerciseLogs
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    if request.method == "POST": # if the request is POST, the user has submitted the form
        exerciseType = request.form.get("exerciseType") # gets the exercise type (cardio or gym) from the form
        exerciseName = request.form.get("exerciseName") # gets the exercise name from the form
        setsVal = request.form.get("sets") # gets the sets from the form
        repsVal = request.form.get("reps") # gets the reps from the form
        durationVal = request.form.get("duration") # gets the duration in minutes (for cardio) from the form
        dateVal = request.form.get("date") # gets the date from the form

        if not exerciseType or exerciseType not in ["gym", "cardio"]: # validate exercise type was selected
            flash("Please select an exercise type (Gym or Cardio).", "error")
            nameList, _ = get_all_exercise_names_and_ids()
            return render_template("exercise_log.html", exerciseNames=nameList)

        if not exerciseName: # validate exercise name was selected
            flash("Please select an exercise.", "error")
            nameList, _ = get_all_exercise_names_and_ids()
            return render_template("exercise_log.html", exerciseNames=nameList)

        if not dateVal or dateVal.strip() == "": # validate date is provided
            flash("Please enter a date.", "error")
            nameList, _ = get_all_exercise_names_and_ids()
            return render_template("exercise_log.html", exerciseNames=nameList)
        
        try: # validate date is between 1900 and 2200
            dateObj = datetime.datetime.strptime(dateVal, "%Y-%m-%d")
            if dateObj.year < 1900 or dateObj.year > 2200:
                flash("Year must be between 1900 and 2200.", "error")
                nameList, _ = get_all_exercise_names_and_ids()
                return render_template("exercise_log.html", exerciseNames=nameList)
        except ValueError:
            flash("Please enter a valid date.", "error")
            nameList, _ = get_all_exercise_names_and_ids()
            return render_template("exercise_log.html", exerciseNames=nameList)

        if exerciseType == "gym": # validate fields based on exercise type (gym needs weight, sets, reps)
            weightVal = request.form.get("weight") # gets the weight from the form
            if not weightVal or not setsVal or not repsVal:
                flash("Please enter weight, sets and reps for gym exercises.", "error")
                nameList, _ = get_all_exercise_names_and_ids()
                return render_template("exercise_log.html", exerciseNames=nameList)
            try:
                weightFloat = float(weightVal)
                setsInt = int(setsVal)
                repsInt = int(repsVal)
                if weightFloat < 0.1:
                    flash("Weight must be at least 0.1 kg.", "error")
                    nameList, _ = get_all_exercise_names_and_ids()
                    return render_template("exercise_log.html", exerciseNames=nameList)
                if setsInt < 1 or repsInt < 1:
                    flash("Sets and reps must be at least 1.", "error")
                    nameList, _ = get_all_exercise_names_and_ids()
                    return render_template("exercise_log.html", exerciseNames=nameList)
            except (ValueError, TypeError):
                flash("Invalid number format for weight, sets or reps.", "error")
                nameList, _ = get_all_exercise_names_and_ids()
                return render_template("exercise_log.html", exerciseNames=nameList)
            durationFloat = None
        else: # cardio: validate duration is provided
            if not durationVal:
                flash("Please enter duration for cardio exercises.", "error")
                nameList, _ = get_all_exercise_names_and_ids()
                return render_template("exercise_log.html", exerciseNames=nameList)
            try:
                durationFloat = float(durationVal)
                if durationFloat < 1:
                    flash("Duration must be at least 1 minute.", "error")
                    nameList, _ = get_all_exercise_names_and_ids()
                    return render_template("exercise_log.html", exerciseNames=nameList)
            except (ValueError, TypeError):
                flash("Invalid number format for duration.", "error")
                nameList, _ = get_all_exercise_names_and_ids()
                return render_template("exercise_log.html", exerciseNames=nameList)
            setsInt = None
            repsInt = None

        nameList, idList = get_all_exercise_names_and_ids() # get sorted lists of exercise names and ids
        index = binSearch(nameList, exerciseName) # use binary search to find the index of the chosen exercise. uses binary search function i created
        if index == -1:
            flash("Exercise not found. Please choose an exercise from the list.", "error")
            nameList, _ = get_all_exercise_names_and_ids()
            return render_template("exercise_log.html", exerciseNames=nameList)

        exerciseId = idList[index] # gets the exercise id from the id list

        cursor.execute(
            "SELECT metValue FROM exercises WHERE exerciseId = ?;",
            (exerciseId,),
        ) # executes SQL query to get the MET value for this exercise
        row = cursor.fetchone() # fetches the row from the database
        if row is None:
            flash("Could not find MET value for this exercise.", "error") # displays error message to the user
            nameList, _ = get_all_exercise_names_and_ids()
            return render_template("exercise_log.html", exerciseNames=nameList)

        metValue = row["metValue"] # gets the MET value from the row

        cursor.execute(
            "SELECT weight FROM bodyWeight WHERE userId = ? ORDER BY date DESC LIMIT 1;",
            (session["userId"],)
        ) # executes SQL query to get the user's most recent weight for calorie calculation
        weightRow = cursor.fetchone() # fetches the row from the database
        userWeightKg = weightRow["weight"] if weightRow else 70.0 # uses 70 kg default if no weight logged

        if exerciseType == "cardio": # for cardio use duration; for gym estimate duration from sets and reps
            hours = durationFloat / 60.0
        else: # gym: estimate duration (each rep ~3 sec, 60 sec rest per set)
            estimatedSeconds = (setsInt * repsInt * 3) + (setsInt * 60)
            hours = estimatedSeconds / 3600.0

        caloriesBurned = round(metValue * userWeightKg * hours, 1) # simple formula: MET * weight(kg) * time(hours)

        if not dateVal or dateVal.strip() == "":
            dateVal = currentTime() # if no date given, use current time string

        cursor.execute(
            """
            INSERT INTO exerciseLogs (userId, exerciseId, date, sets, reps, weight, duration, caloriesBurned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                session["userId"],
                exerciseId,
                dateVal,
                setsInt,
                repsInt,
                weightFloat if exerciseType == "gym" else None,
                durationFloat,
                caloriesBurned,
            ),
        ) # executes SQL query to insert the exercise log entry
        db.commit() # saves the changes to the database

        flash(f"Exercise logged. Estimated calories burned: {caloriesBurned} cal", "success") # displays success message to the user
        return redirect(url_for("dashboard.home")) # redirects the user to the dashboard

    nameList, _ = get_all_exercise_names_and_ids() # for GET, load all exercises for the select box
    return render_template("exercise_log.html", exerciseNames=nameList) # renders the exercise log template


@exercise_bp.route("/exercise/list") # route for getting exercise list as JSON (optionally by type)
def list_exercises(): # function to return all exercises or filtered by type as JSON
    """
    returns a JSON list of all exercises, optionally filtered by type (gym or cardio). used for autocomplete or search.
    """
    exerciseType = request.args.get("type") # gets the optional type filter (gym or cardio) from the request

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    if exerciseType:
        cursor.execute(
            "SELECT exerciseId, exerciseName FROM exercises WHERE exerciseType = ? ORDER BY exerciseName ASC;",
            (exerciseType,)
        ) # executes SQL query to get exercises filtered by type
    else:
        cursor.execute("SELECT exerciseId, exerciseName FROM exercises ORDER BY exerciseName ASC;") # executes SQL query to get all exercises

    rows = cursor.fetchall() # fetches all rows from the database
    result = [] # creates an empty list to store the data
    for row in rows:
        result.append({"exerciseId": row["exerciseId"], "exerciseName": row["exerciseName"]}) # appends each row as a dict
    return jsonify(result) # returns the list as JSON


@exercise_bp.route("/exercise/presets", methods=["GET"]) # route for listing workout presets as JSON
def list_presets(): # function to return all workout presets for the current user as JSON
    """
    returns all workout presets for the current user as JSON.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT id, presetName FROM workoutPresets WHERE userId = ? ORDER BY createdAt DESC;",
        (session["userId"],),
    ) # executes SQL query to get all presets for the user
    rows = cursor.fetchall() # fetches all rows from the database
    presets = [] # creates an empty list to store the presets
    for row in rows:
        presets.append({"id": row["id"], "presetName": row["presetName"]}) # appends each row as a dict

    return jsonify(presets) # returns the presets as JSON


@exercise_bp.route("/exercise/workouts", methods=["GET", "POST"]) # route for workouts page (create and edit presets)
def workouts_page(): # function to show workouts page (GET) or handle create/add/delete actions (POST)
    """
    workouts page. GET shows all workouts and exercise names; POST handles create, add_exercise, delete_exercise, delete.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    if request.method == "POST": # if the request is POST, handle the form action
        action = request.form.get("action") # gets the action from the form (create, add_exercise, delete_exercise, delete)
        
        if action == "create":
            presetName = request.form.get("presetName")
            if not presetName:
                flash("Please enter a workout name.", "error")
                return redirect(url_for("exercise.workouts_page"))
            
            workoutPreset = WorkoutPreset(presetName)
            workoutPreset.savetoDB(session["userId"])
            flash(f"Workout '{presetName}' created. You can now add exercises to it.", "success")
        
        elif action == "add_exercise":
            presetId = int(request.form.get("presetId"))
            exerciseName = request.form.get("exerciseName")
            exerciseType = request.form.get("exerciseType")
            
            cursor.execute("SELECT id FROM workoutPresets WHERE id = ? AND userId = ?;", (presetId, session["userId"])) # verify the workout belongs to the user
            if cursor.fetchone():
                workoutPreset = WorkoutPreset.loadFromDB(presetId)
                if workoutPreset:
                    if exerciseType == "cardio":
                        durationVal = float(request.form.get("duration") or 0)
                        presetExercise = ExercisePreset(
                            exerciseName,
                            setsValue=None,
                            repsValue=None,
                            weightValue=None,
                            durationValue=durationVal
                        )
                    else:  # gym
                        setsVal = int(request.form.get("sets") or 0)
                        repsVal = int(request.form.get("reps") or 0)
                        weightVal = float(request.form.get("weight") or 0)
                        presetExercise = ExercisePreset(
                            exerciseName,
                            setsValue=setsVal,
                            repsValue=repsVal,
                            weightValue=weightVal,
                            durationValue=None
                        )
                    workoutPreset.add_exercise(presetExercise)
                    workoutPreset.savetoDB(session["userId"])
                    flash("Exercise added to workout.", "success")
                else:
                    flash("Workout not found.", "error")
            else:
                flash("Workout not found or access denied.", "error")
        
        elif action == "delete_exercise":
            presetId = int(request.form.get("presetId"))
            exerciseIndex = int(request.form.get("exerciseIndex", -1))
            if exerciseIndex < 0:
                flash("Invalid exercise index.", "error")
                return redirect(url_for("exercise.workouts_page"))
            cursor.execute("SELECT id FROM workoutPresets WHERE id = ? AND userId = ?;", (presetId, session["userId"]))
            if not cursor.fetchone():
                flash("Workout not found or access denied.", "error")
                return redirect(url_for("exercise.workouts_page"))
            workoutPreset = WorkoutPreset.loadFromDB(presetId)
            if workoutPreset and 0 <= exerciseIndex < len(workoutPreset.exerciseList):
                workoutPreset.exerciseList.remove_at(exerciseIndex)  # uses Stack Operations (remove_at) from data_structures.py to remove the exercise at the given index
                workoutPreset.savetoDB(session["userId"])
                flash("Exercise removed from workout.", "success")
            else:
                flash("Exercise or workout not found.", "error")

        elif action == "delete":
            presetId = int(request.form.get("presetId"))
            cursor.execute("DELETE FROM workoutPresets WHERE id = ? AND userId = ?;", (presetId, session["userId"]))
            db.commit()
            flash("Workout deleted.", "success")
        
        return redirect(url_for("exercise.workouts_page")) # redirects the user to the workouts page

    cursor.execute( # GET request: load all workouts for the user
        "SELECT id, presetName, createdAt FROM workoutPresets WHERE userId = ? ORDER BY createdAt DESC;",
        (session["userId"],),
    ) # executes SQL query to get all workout presets for the user
    rows = cursor.fetchall() # fetches all rows from the database

    workouts = [] # creates an empty list to store the workout presets
    for row in rows:
        workoutPreset = WorkoutPreset.loadFromDB(row["id"]) # loads the full preset from the database
        if workoutPreset:
            workouts.append(workoutPreset) # appends the preset to the list

    nameList, _ = get_all_exercise_names_and_ids() # gets all exercise names for the dropdown
    return render_template("workouts.html", workouts=workouts, exerciseNames=nameList) # renders the workouts template


@exercise_bp.route("/exercise/preset/use/<int:preset_id>", methods=["GET"]) # route for loading a preset onto the exercise log page
def use_preset(preset_id): # function to load a preset and show it on the exercise log (user can adjust without changing original)
    """
    loads a preset and shows it on the exercise log page. user can adjust sets/reps/weight for this session without changing the original.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    preset = WorkoutPreset.loadFromDB(preset_id) # loads the preset from the database
    if preset is None:
        flash("Preset not found.", "error") # displays error message to the user
        return redirect(url_for("dashboard.home")) # redirects the user to the dashboard

    preset_instance = PresetInstance(preset) # creates a PresetInstance so the user can modify without changing the original

    nameList, _ = get_all_exercise_names_and_ids() # gets the full list of exercise names for the select box
    return render_template(
        "exercise_log.html",
        exerciseNames=nameList,
        preset=preset_instance,
    ) # renders the exercise log template with the preset


@exercise_bp.route("/exercise/log/workout/<int:preset_id>", methods=["POST"]) # route for logging a full workout from a preset
def log_workout(preset_id): # function to log all exercises from a preset as separate exercise log entries
    """
    logs all exercises from a workout preset as separate exercise log entries. uses form values (or preset defaults) and the same date.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    dateVal = request.form.get("date") # gets the date from the form
    if not dateVal or dateVal.strip() == "":
        flash("Please enter a date.", "error") # displays error message to the user
        return redirect(url_for("exercise.exercise_log")) # redirects the user to the exercise log page

    try: # validate date is between 1900 and 2200
        dateObj = datetime.datetime.strptime(dateVal, "%Y-%m-%d")
        if dateObj.year < 1900 or dateObj.year > 2200:
            flash("Year must be between 1900 and 2200.", "error")
            return redirect(url_for("exercise.exercise_log"))
    except ValueError:
        flash("Please enter a valid date.", "error")
        return redirect(url_for("exercise.exercise_log"))

    preset = WorkoutPreset.loadFromDB(preset_id) # loads the preset from the database
    if preset is None:
        flash("Workout not found.", "error")
        return redirect(url_for("exercise.exercise_log"))

    cursor.execute(
        "SELECT weight FROM bodyWeight WHERE userId = ? ORDER BY date DESC LIMIT 1;",
        (session["userId"],)
    ) # executes SQL query to get user weight for calorie calculation
    weightRow = cursor.fetchone() # fetches the row from the database
    userWeightKg = weightRow["weight"] if weightRow else 70.0

    nameList, idList = get_all_exercise_names_and_ids() # gets exercise names and ids

    form_exercises = [] # builds list of exercises from form (edited/deleted items respected)
    i = 0
    while True:
        exerciseName = request.form.get(f"exerciseName_{i}")
        if not exerciseName:
            break
        exerciseType = request.form.get(f"exerciseType_{i}")
        form_exercises.append({
            "name": exerciseName,
            "type": exerciseType,
            "sets": request.form.get(f"sets_{i}"),
            "reps": request.form.get(f"reps_{i}"),
            "weight": request.form.get(f"weight_{i}"),
            "duration": request.form.get(f"duration_{i}"),
        })
        i += 1
    if not form_exercises: # if form had no exercise indices (e.g. JS re-index not run), fall back to preset
        for ex in preset.exerciseList:
            exerciseType = "cardio" if ex.durationValue else "gym"
            form_exercises.append({
                "name": ex.exerciseName,
                "type": exerciseType,
                "sets": str(ex.setsValue) if ex.setsValue is not None else "",
                "reps": str(ex.repsValue) if ex.repsValue is not None else "",
                "weight": str(ex.weightValue) if ex.weightValue is not None else "",
                "duration": str(ex.durationValue) if ex.durationValue is not None else "",
            })
    
    exercises_logged = 0
    for data in form_exercises:
        exerciseName = data["name"]
        exerciseType = data["type"] or ("cardio" if data["duration"] else "gym")
        
        if exerciseType == "gym":
            setsVal = data["sets"]
            repsVal = data["reps"]
            weightVal = data["weight"]
            try:
                setsInt = int(setsVal) if setsVal else 0
                repsInt = int(repsVal) if repsVal else 0
                weightFloat = float(weightVal) if weightVal else 0.0
            except (ValueError, TypeError):
                flash(f"Invalid values for '{exerciseName}'. Skipping.", "error")
                continue
            if setsInt < 1 or repsInt < 1:
                flash(f"Sets and reps must be at least 1 for '{exerciseName}'. Skipping.", "error")
                continue
            durationFloat = None
        else:
            durationVal = data["duration"]
            try:
                durationFloat = float(durationVal) if durationVal else 0.0
            except (ValueError, TypeError):
                flash(f"Invalid duration for '{exerciseName}'. Skipping.", "error")
                continue
            if durationFloat < 1:
                flash(f"Duration must be at least 1 minute for '{exerciseName}'. Skipping.", "error")
                continue
            setsInt = None
            repsInt = None
            weightFloat = None
        
        idx = binSearch(nameList, exerciseName)
        if idx == -1:
            flash(f"Exercise '{exerciseName}' not found. Skipping.", "error")
            continue
        exerciseId = idList[idx]
        
        cursor.execute(
            "SELECT metValue, exerciseType FROM exercises WHERE exerciseId = ?;",
            (exerciseId,),
        )
        row = cursor.fetchone()
        if row is None:
            flash(f"Could not find MET value for '{exerciseName}'. Skipping.", "error")
            continue
        metValue = row["metValue"]
        
        if exerciseType == "cardio":
            hours = durationFloat / 60.0
        else:
            estimatedSeconds = (setsInt * repsInt * 3) + (setsInt * 60)
            hours = estimatedSeconds / 3600.0
        caloriesBurned = round(metValue * userWeightKg * hours, 1)
        
        cursor.execute(
            """
            INSERT INTO exerciseLogs (userId, exerciseId, date, sets, reps, weight, duration, caloriesBurned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                session["userId"],
                exerciseId,
                dateVal,
                setsInt,
                repsInt,
                weightFloat,
                durationFloat,
                caloriesBurned,
            ),
        )
        exercises_logged += 1
    
    db.commit() # saves the changes to the database

    if exercises_logged > 0:
        flash(f"Workout logged successfully. {exercises_logged} exercise(s) saved.", "success") # displays success message to the user
    else:
        flash("No exercises were logged.", "error") # displays error message to the user

    return redirect(url_for("dashboard.home")) # redirects the user to the dashboard


@exercise_bp.route("/exercise/log/edit/<int:log_id>", methods=["GET", "POST"]) # route for editing an exercise log entry
def edit_exercise_log(log_id): # function to show edit form (GET) or update the entry (POST)
    """
    edits a single exercise log. GET shows the form with current data; POST updates the entry in the database.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        """
        SELECT el.logId, el.exerciseId, el.date, el.sets, el.reps, el.weight, el.duration, e.exerciseName
        FROM exerciseLogs el
        JOIN exercises e ON el.exerciseId = e.exerciseId
        WHERE el.userId = ? AND el.logId = ?;
        """,
        (session["userId"], log_id)
    ) # executes SQL query to get the exercise log entry. uses cross-table parameterised SQL
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Exercise log not found.", "error") # displays error message to the user
        return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar
    if request.method == "POST": # if the request is POST, update the log
        setsVal = request.form.get("sets")
        repsVal = request.form.get("reps")
        weightVal = request.form.get("weight")
        durationVal = request.form.get("duration")
        dateVal = request.form.get("date") or row["date"]
        try:
            setsInt = int(setsVal) if setsVal else None
            repsInt = int(repsVal) if repsVal else None
            weightFloat = float(weightVal) if weightVal else None
            durationFloat = float(durationVal) if durationVal else None
        except (ValueError, TypeError):
            flash("Invalid numbers.", "error")
            return redirect(url_for("exercise.edit_exercise_log", log_id=log_id))
        cursor.execute(
            "SELECT metValue, exerciseType FROM exercises WHERE exerciseId = ?;",
            (row["exerciseId"],)
        )
        exRow = cursor.fetchone()
        metValue = exRow["metValue"] if exRow else 5.0
        exerciseType = exRow["exerciseType"] if exRow else "gym"
        cursor.execute(
            "SELECT weight FROM bodyWeight WHERE userId = ? ORDER BY date DESC LIMIT 1;",
            (session["userId"],)
        )
        weightRow = cursor.fetchone()
        userWeightKg = weightRow["weight"] if weightRow else 70.0
        if exerciseType == "cardio":
            hours = (durationFloat or 0) / 60.0
        else:
            setsInt = setsInt or 0
            repsInt = repsInt or 0
            estimatedSeconds = (setsInt * repsInt * 3) + (setsInt * 60) if (setsInt and repsInt) else 0
            hours = estimatedSeconds / 3600.0
        caloriesBurned = round(metValue * userWeightKg * hours, 1)
        cursor.execute(
            """
            UPDATE exerciseLogs SET sets = ?, reps = ?, weight = ?, duration = ?, date = ?, caloriesBurned = ?
            WHERE logId = ? AND userId = ?;
            """,
            (setsInt, repsInt, weightFloat, durationFloat, dateVal, caloriesBurned, log_id, session["userId"])
        ) # executes SQL query to update the exercise log entry
        db.commit() # saves the changes to the database
        flash("Exercise log updated.", "success") # displays success message to the user
        return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar
    return render_template("exercise_log_edit.html", log=dict(row), log_id=log_id) # GET: render the edit template with the log data


@exercise_bp.route("/exercise/log/delete/<int:log_id>", methods=["POST"]) # route for deleting an exercise log entry
def delete_exercise_log(log_id): # function to delete the exercise log entry from the database
    """
    deletes a single exercise log entry.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("DELETE FROM exerciseLogs WHERE logId = ? AND userId = ?;", (log_id, session["userId"])) # executes SQL query to delete the entry
    db.commit() # saves the changes to the database
    flash("Exercise log deleted.", "success") # displays success message to the user
    return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar
