# routes for exercise logging, exercise list, presets, workouts and calendar log endpoints

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify
import datetime

from ..utils.db import currentTime
from ..utils.search import binSearch
from ..models.preset import WorkoutPreset, ExercisePreset, PresetInstance


# blueprint for all exercise related pages and API endpoints
exercise_bp = Blueprint("exercise", __name__)


def getAll(): # helper to load all exercise names and ids from the database
    """
    reads all exercise names from the database and returns sorted name list and parallel id list.
    the id list is used so that after binary search on names we can get the correct exerciseId.
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


def getExercisesWithType(): # function to load all exercises with name and type for the log form dropdown (filter by type in JS)
    """Returns list of dicts with 'name' and 'type' (gym/cardio) for template dropdown; JS filters by selected type."""
    db = g.db
    cursor = db.cursor()
    cursor.execute("SELECT exerciseName, exerciseType FROM exercises ORDER BY exerciseName ASC;")
    rows = cursor.fetchall()
    return [{"name": row["exerciseName"], "type": row["exerciseType"]} for row in rows]


@exercise_bp.route("/exercise/log", methods=["GET", "POST"], endpoint="exercise_log") # route for logging an exercise session
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
        exerciseType = request.form.get("exerciseType") or request.form.get("exercise_type") # gets the exercise type (cardio or gym) from the form
        exerciseName = request.form.get("exerciseName") # gets the exercise name from the form
        setsVal = request.form.get("sets") # gets the sets from the form
        repsVal = request.form.get("reps") # gets the reps from the form
        durationVal = request.form.get("duration") # gets the duration in minutes (for cardio) from the form
        dateVal = request.form.get("date") # gets the date from the form

        if not exerciseType or exerciseType not in ["gym", "cardio"]: # if the exercise type is not selected or is not gym or cardio
            flash("Please select an exercise type (Gym or Cardio).", "error")# displays error message to the user
            nameList, _ = getAll()# gets the list of exercise names and ids
            return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType())# renders the exercise log template with the list of exercise names and ids

        if not exerciseName: # if the exercise name is not selected
            flash("Please select an exercise.", "error") # displays error message to the user
            nameList, _ = getAll()# gets the list of exercise names and ids
            return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType())# renders the exercise log template with the list of exercise names and ids

        if not dateVal or dateVal.strip() == "": # if the date is not provided
            flash("Please enter a date.", "error") # displays error message to the user
            nameList, _ = getAll()# gets the list of exercise names and ids
            return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType())# renders the exercise log template with the list of exercise names and ids
        
        try: # if the date is between 1900 and 2200
            dateObj = datetime.datetime.strptime(dateVal, "%Y-%m-%d") # converts the date to a datetime object (correct format YYYY-MM-DD)
            if dateObj.year < 1900 or dateObj.year > 2200: # if the year is not between 1900 and 2200  
                flash("Year must be between 1900 and 2200.", "error") # displays error message to the user
                nameList, _ = getAll() # gets the list of exercise names and ids
                return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType())# renders the exercise log template with the list of exercise names and ids
        except ValueError: # if the date is not a valid date
            flash("Please enter a valid date.", "error") # displays error message to the user
            nameList, _ = getAll() # gets the list of exercise names and ids
            return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType())# renders the exercise log template with the list of exercise names and ids

        if exerciseType == "gym": # if the exercise type is gym
            weightVal = request.form.get("weight") # gets the weight from the form
            if not weightVal or not setsVal or not repsVal: # if the weight, sets or reps are not provided
                flash("Please enter weight, sets and reps for gym exercises.", "error") # displays error message to the user
                nameList, _ = getAll() # gets the list of exercise names and ids
                return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids
            try:
                weightFloat = float(weightVal) # converts the weight to a float
                setsInt = int(setsVal) # converts the sets to an integer
                repsInt = int(repsVal) # converts the reps to an integer
                if weightFloat < 0.1: # if the weight is less than 0.1 kg, display error message
                    flash("Weight must be at least 0.1 kg.", "error")
                    nameList, _ = getAll()
                    return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids
                if setsInt < 1 or repsInt < 1: # if the sets or reps are less than 1, display error message
                    flash("Sets and reps must be at least 1.", "error")
                    nameList, _ = getAll() # gets the list of exercise names and ids
                    return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids
            except (ValueError, TypeError): # if the weight, sets or reps are not a valid number, display error message
                flash("Invalid number format for weight, sets or reps.", "error")
                nameList, _ = getAll() # gets the list of exercise names and ids
                return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids
            durationFloat = None # sets the duration to None
        else: # (cardio). validates duration provided
            if not durationVal: # if the duration is not provided, display error message
                flash("Please enter duration for cardio exercises.", "error")
                nameList, _ = getAll() # gets the list of exercise names and ids
                return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids
            try:
                durationFloat = float(durationVal) # converts the duration to a float
                if durationFloat < 1: # if the duration is less than 1 minute, display error message
                    flash("Duration must be at least 1 minute.", "error")
                    nameList, _ = getAll() # gets the list of exercise names and ids
                    return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType())
            except (ValueError, TypeError): # if the duration is not a valid number, display error message
                flash("Invalid number format for duration.", "error")
                nameList, _ = getAll() # gets the list of exercise names and ids
                return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids
            setsInt = None # sets the sets to None
            repsInt = None # sets the reps to None

        nameList, idList = getAll() # get sorted lists of exercise names and ids
        index = binSearch(nameList, exerciseName) # use binary search to find the index of the chosen exercise. uses binary search function i created
        if index == -1: # if the exercise is not found, display error message
            flash("Exercise not found. Please choose an exercise from the list.", "error")
            nameList, _ = getAll() # gets the list of exercise names and ids
            return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids

        exerciseId = idList[index] # gets the exercise id from the id list

        cursor.execute(
            "SELECT metValue FROM exercises WHERE exerciseId = ?;",
            (exerciseId,),
        ) # executes SQL query to get the MET value for this exercise
        row = cursor.fetchone() # fetches the row from the database
        if row is None: # if the MET value is not found, display error message
            flash("Could not find MET value for this exercise.", "error") # displays error message to the user
            nameList, _ = getAll() # gets the list of exercise names and ids
            return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=getExercisesWithType()) # renders the exercise log template with the list of exercise names and ids

        metValue = row["metValue"] # gets the MET value from the row

        cursor.execute(
            "SELECT weight FROM bodyWeight WHERE userId = ? ORDER BY date DESC LIMIT 1;",
            (session["userId"],)
        ) # executes SQL query to get the user's most recent weight for calorie calculation
        weightRow = cursor.fetchone() # fetches the row from the database
        userWeightKg = weightRow["weight"] if weightRow else 70.0 # uses 70 kg default if no weight logged

        if exerciseType == "cardio": # for cardio use duration; for gym estimate duration from sets and reps
            hours = durationFloat / 60.0
        else: # gym: estimate duration (each rep ~3 sec, 60 sec rest per set), approximating for simplicity
            estimatedSeconds = (setsInt * repsInt * 3) + (setsInt * 60)
            hours = estimatedSeconds / 3600.0

        caloriesBurned = round(metValue * userWeightKg * hours, 1) # MET * weight(kg) * time(hours)

        if not dateVal or dateVal.strip() == "": # if no date given, use current time string
            dateVal = currentTime() 

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

    nameList, _ = getAll() # for GET, load all exercises for the select box
    exerciseList = getExercisesWithType() # name + type for dropdown; JS filters by type
    return render_template("exercise_log.html", exerciseNames=nameList, exerciseList=exerciseList) # renders the exercise log template


@exercise_bp.route("/exercise/list") # route for getting exercise list as JSON
def listExercise(): # function to return all exercises filtered by type as JSON
 
    exerciseType = request.args.get("type") # gets the type filter (gym or cardio) from the request

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
        name = row["exerciseName"] # gets the exercise name from the row
        result.append({"exerciseId": row["exerciseId"], "exerciseName": name, "exercise_name": name}) # appends the exercise id, name and exercise name to the list
    return jsonify(result) # returns the list as JSON


@exercise_bp.route("/exercise/presets", methods=["GET"]) # route for listing workout presets as JSON
def listPresets(): # function to return all workout presets for the current user as JSON

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
        name = row["presetName"] # gets the preset name from the row
        presets.append({"id": row["id"], "presetName": name, "preset_name": name}) # appends the preset id, name and preset name to the list

    return jsonify(presets) # returns the presets as JSON


@exercise_bp.route("/exercise/workouts", methods=["GET", "POST"]) # route for workouts page (create and edit presets)
def workouts_page(): # function to show workouts page (GET) or handle create/add/delete actions (POST)

    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    if request.method == "POST": # if the request is POST, handle the form action
        action = request.form.get("action") # gets the action from the form (create, add_exercise, delete_exercise, delete)
        
        if action == "create": # if the action is create, create a new workout preset
            presetName = request.form.get("presetName") or request.form.get("preset_name") # gets the preset name from the form
            if not presetName: # if the preset name is not provided, display error message
                flash("Please enter a workout name.", "error")
                return redirect(url_for("exercise.workouts_page")) # redirects the user to the workouts page
            
            workoutPreset = WorkoutPreset(presetName) # creates a new workout preset
            workoutPreset.savetoDB(session["userId"]) # saves the workout preset to the database
            flash(f"Workout '{presetName}' created. You can now add exercises to it.", "success") # displays success message to the user
        
        elif action == "add_exercise": # if the action is add_exercise, add an exercise to the workout preset
            presetId = int(request.form.get("presetId")) # gets the preset id from the form
            exerciseName = request.form.get("exerciseName") # gets the exercise name from the form
            exerciseType = request.form.get("exerciseType") # gets the exercise type from the form
            
            cursor.execute("SELECT id FROM workoutPresets WHERE id = ? AND userId = ?;", (presetId, session["userId"])) # executes SQL query to verify the workout belongs to the user
            if cursor.fetchone(): # if the workout belongs to the user
                workoutPreset = WorkoutPreset.loadFromDB(presetId) # loads the workout preset from the database
                if workoutPreset: # if the workout preset is found
                    if exerciseType == "cardio": # if the exercise type is cardio
                        durationVal = float(request.form.get("duration") or 0) # gets the duration from the form
                        presetExercise = ExercisePreset(
                            exerciseName,
                            setsValue=None,
                            repsValue=None,
                            weightValue=None,
                            durationValue=durationVal
                        )
                    else:  # gym
                        setsVal = int(request.form.get("sets") or 0) # gets the sets from the form
                        repsVal = int(request.form.get("reps") or 0) # gets the reps from the form
                        weightVal = float(request.form.get("weight") or 0) # gets the weight from the form
                        presetExercise = ExercisePreset(
                            exerciseName,
                            setsValue=setsVal,
                            repsValue=repsVal,
                            weightValue=weightVal,
                            durationValue=None
                        )
                    workoutPreset.add_exercise(presetExercise) # adds the exercise to the workout preset
                    workoutPreset.savetoDB(session["userId"]) # saves the workout preset to the database
                    flash("Exercise added to workout.", "success")
                else: # if the workout preset is not found, display error message
                    flash("Workout not found.", "error")
            else: # if the workout preset is not found or access denied, display error message
                flash("Workout not found or access denied.", "error")
        
        elif action == "delete_exercise": # if the action is delete_exercise, delete an exercise from the workout preset
            presetId = int(request.form.get("presetId")) # gets the preset id from the form
            exerciseIndex = int(request.form.get("exerciseIndex", -1)) # gets the exercise index from the form
            if exerciseIndex < 0: # if the exercise index is less than 0, display error message
                flash("Invalid exercise index.", "error")
                return redirect(url_for("exercise.workouts_page")) # redirects the user to the workouts page
            cursor.execute("SELECT id FROM workoutPresets WHERE id = ? AND userId = ?;", (presetId, session["userId"])) # executes SQL query to verify the workout belongs to the user
            if not cursor.fetchone(): # if the workout does not belong to the user, display error message
                flash("Workout not found or access denied.", "error")
                return redirect(url_for("exercise.workouts_page")) # redirects the user to the workouts page
            workoutPreset = WorkoutPreset.loadFromDB(presetId) # loads the workout preset from the database
            if workoutPreset and 0 <= exerciseIndex < len(workoutPreset.exerciseList):
                workoutPreset.exerciseList.remove_at(exerciseIndex)  # uses Stack Operations (remove_at) from data_structures.py to remove the exercise at the given index
                workoutPreset.savetoDB(session["userId"]) # saves the workout preset to the database
                flash("Exercise removed from workout.", "success") # displays success message to the user
            else: # if the exercise or workout is not found, display error message
                flash("Exercise or workout not found.", "error")

        elif action == "delete": # if the action is delete, delete the workout preset
            presetId = int(request.form.get("presetId")) # gets the preset id from the form
            cursor.execute("DELETE FROM workoutPresets WHERE id = ? AND userId = ?;", (presetId, session["userId"]))
            db.commit() # saves the changes to the database
            flash("Workout deleted.", "success") # displays success message to the user
        
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

    nameList, _ = getAll() # gets all exercise names for the dropdown
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

    nameList, _ = getAll()
    exerciseList = getExercisesWithType()
    return render_template(
        "exercise_log.html",
        exerciseNames=nameList,
        exerciseList=exerciseList,
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

    nameList, idList = getAll() # gets exercise names and ids

    form_exercises = [] # builds list of exercises from form (edited/deleted items respected)
    i = 0 # starts the index at 0
    while True: # while the index is less than the number of exercises
        exerciseName = request.form.get(f"exerciseName_{i}") # gets the exercise name from the form
        if not exerciseName or (isinstance(exerciseName, str) and exerciseName.strip() in ("", "undefined")): # skip missing or JS "undefined"
            break
        exerciseType = request.form.get(f"exerciseType_{i}") # gets the exercise type from the form
        form_exercises.append({ # appends the exercise to the list
            "name": exerciseName,
            "type": exerciseType,
            "sets": request.form.get(f"sets_{i}"), # gets the sets from the form
            "reps": request.form.get(f"reps_{i}"), # gets the reps from the form
            "weight": request.form.get(f"weight_{i}"), # gets the weight from the form
            "duration": request.form.get(f"duration_{i}"), # gets the duration from the form
        })
        i += 1 # increments the index by 1
    if not form_exercises: # if form had no exercise indices (e.g. JS re-index not run), fall back to preset
        for ex in preset.exerciseList: # for each exercise in the preset
            name = (ex.exerciseName or "").strip() if ex.exerciseName else ""
            if not name:
                continue
            exerciseType = "cardio" if ex.durationValue else "gym"
            form_exercises.append({ # appends the exercise to the list
                "name": name,
                "type": exerciseType,
                "sets": str(ex.setsValue) if ex.setsValue is not None else "", # gets the sets from the exercise
                "reps": str(ex.repsValue) if ex.repsValue is not None else "", # gets the reps from the exercise
                "weight": str(ex.weightValue) if ex.weightValue is not None else "", # gets the weight from the exercise
                "duration": str(ex.durationValue) if ex.durationValue is not None else "", # gets the duration from the exercise
            })
    
    exercises_logged = 0 # starts the number of exercises logged at 0
    for data in form_exercises:
        exerciseName = data.get("name") or "" # gets the exercise name from the form
        if not exerciseName or (isinstance(exerciseName, str) and exerciseName.strip() == "undefined"):
            continue # skip invalid names (undefined strings)
        exerciseType = data["type"] or ("cardio" if data["duration"] else "gym") # gets the exercise type from the form
        
        if exerciseType == "gym": # if the exercise type is gym
            setsVal = data["sets"] # gets the sets from the form
            repsVal = data["reps"] # gets the reps from the form
            weightVal = data["weight"] # gets the weight from the form
            try: # try to convert the sets, reps and weight to integers and floats
                setsInt = int(setsVal) if setsVal else 0 # converts the sets to an integer
                repsInt = int(repsVal) if repsVal else 0 # converts the reps to an integer
                weightFloat = float(weightVal) if weightVal else 0.0 # converts the weight to a float
            except (ValueError, TypeError): # if the sets, reps or weight are not a valid number, display error message
                flash(f"Invalid values for '{exerciseName}'. Skipping.", "error")
                continue # continue to the next exercise
            if setsInt < 1 or repsInt < 1:
                flash(f"Sets and reps must be at least 1 for '{exerciseName}'. Skipping.", "error")
                continue # continue to the next exercise    
            durationFloat = None # sets the duration to None
        else: # if the exercise type is cardio
            durationVal = data["duration"] # gets the duration from the form
            try: # try to convert the duration to a float
                durationFloat = float(durationVal) if durationVal else 0.0 # converts the duration to a float
            except (ValueError, TypeError): # if the duration is not a valid number, display error message
                flash(f"Invalid duration for '{exerciseName}'. Skipping.", "error")
                continue
            if durationFloat < 1: # if the duration is less than 1 minute, display error message
                flash(f"Duration must be at least 1 minute for '{exerciseName}'. Skipping.", "error")
                continue # continue to the next exercise
            setsInt = None # sets the sets to None
            repsInt = None # sets the reps to None
            weightFloat = None # sets the weight to None
        
        idx = binSearch(nameList, exerciseName) # uses binary search to find the index of the exercise in the list
        if idx == -1: # if the exercise is not found, display error message
            flash(f"Exercise '{exerciseName}' not found. Skipping.", "error")
            continue # continue to the next exercise
        exerciseId = idList[idx]
        
        cursor.execute(
            "SELECT metValue, exerciseType FROM exercises WHERE exerciseId = ?;",
            (exerciseId,),
        ) # executes SQL query to get the MET value and exercise type from the database
        row = cursor.fetchone() # fetches the row from the database
        if row is None: # if the row is not found, display error message
            flash(f"Could not find MET value for '{exerciseName}'. Skipping.", "error")
            continue
        metValue = row["metValue"] # gets the MET value from the row
        
        if exerciseType == "cardio": # if the exercise type is cardio
            hours = durationFloat / 60.0
        else: # if the exercise type is gym
            estimatedSeconds = (setsInt * repsInt * 3) + (setsInt * 60) # calculates the estimated seconds
            hours = estimatedSeconds / 3600.0 # calculates the hours
        caloriesBurned = round(metValue * userWeightKg * hours, 1) # calculates the calories burned
        
        cursor.execute( # executes SQL query to insert the exercise log entry into the database
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
        exercises_logged += 1 # increments the number of exercises logged by 1
    
    db.commit() # saves the changes to the database

    if exercises_logged > 0: # if the number of exercises logged is greater than 0, display success message
        flash(f"Workout logged successfully. {exercises_logged} exercise(s) saved.", "success") # displays success message to the user
    else: # if the number of exercises logged is 0, display error message
        flash("No exercises were logged.", "error") # displays error message to the user

    return redirect(url_for("dashboard.home")) # redirects the user to the dashboard


@exercise_bp.route("/exercise/log/edit/<int:log_id>", methods=["GET", "POST"]) # route for editing an exercise log entry
def edit_exercise_log(log_id): # function to show edit form (GET) or update the entry (POST)
   
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
    ) # executes SQL query to get the exercise log entry. cross-tabular 
    row = cursor.fetchone() # fetches the row from the database
    if row is None:
        flash("Exercise log not found.", "error") # displays error message to the user
        return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar
    if request.method == "POST": # if the request is POST, update the log
        setsVal = request.form.get("sets") # gets the sets from the form
        repsVal = request.form.get("reps") # gets the reps from the form
        weightVal = request.form.get("weight") # gets the weight from the form
        durationVal = request.form.get("duration") # gets the duration from the form
        dateVal = request.form.get("date") or row["date"] # gets the date from the form or the row
        try:
            setsInt = int(setsVal) if setsVal else None # converts the sets to an integer
            repsInt = int(repsVal) if repsVal else None # converts the reps to an integer
            weightFloat = float(weightVal) if weightVal else None # converts the weight to a float
            durationFloat = float(durationVal) if durationVal else None # converts the duration to a float
        except (ValueError, TypeError): # if the sets, reps, weight or duration are not a valid number, display error message
            flash("Invalid numbers.", "error")
            return redirect(url_for("exercise.edit_exercise_log", log_id=log_id)) # redirects the user to the edit exercise log page
        cursor.execute(
            "SELECT metValue, exerciseType FROM exercises WHERE exerciseId = ?;", # executes SQL query to get the MET value and exercise type from the database
            (row["exerciseId"],)
        )
        exRow = cursor.fetchone() # fetches the row from the database
        metValue = exRow["metValue"] if exRow else 5.0 # gets the MET value from the row
        exerciseType = exRow["exerciseType"] if exRow else "gym" # gets the exercise type from the row
        cursor.execute(
            "SELECT weight FROM bodyWeight WHERE userId = ? ORDER BY date DESC LIMIT 1;", # executes SQL query to get the user's most recent weight for calorie calculation
            (session["userId"],)
        )
        weightRow = cursor.fetchone() # fetches the row from the database
        userWeightKg = weightRow["weight"] if weightRow else 70.0 # gets the user's weight from the row or uses 70 kg default
        if exerciseType == "cardio": # if exercise type is cardio
            hours = (durationFloat or 0) / 60.0 # calculates the hours for cardio
        else:
            setsInt = setsInt or 0 # converts the sets to an integer
            repsInt = repsInt or 0 # converts the reps to an integer
            estimatedSeconds = (setsInt * repsInt * 3) + (setsInt * 60) if (setsInt and repsInt) else 0 # calculates the estimated seconds
            hours = estimatedSeconds / 3600.0 # calculates the hours
        caloriesBurned = round(metValue * userWeightKg * hours, 1) # calculates the calories burned
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
   
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute("DELETE FROM exerciseLogs WHERE logId = ? AND userId = ?;", (log_id, session["userId"])) # executes SQL query to delete the entry
    db.commit() # saves the changes to the database
    flash("Exercise log deleted.", "success") # displays success message to the user
    return redirect(url_for("dashboard.calendar")) # redirects the user to the calendar
