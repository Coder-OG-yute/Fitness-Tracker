# module containing blueprint for analytics page and JSON endpoints for graphs


from datetime import datetime, timedelta

from flask import Blueprint, jsonify, session, redirect, url_for, g, render_template, request


analytics_bp = Blueprint("analytics", __name__) # blueprint for analytics page and navigation


@analytics_bp.route("/analytics") # route for analytics page
def analytics_page(): # function to render the analytics page
    #analytics page that can hold multiple charts.
    
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    return render_template("analytics.html") # render the analytics page


@analytics_bp.route("/analytics/weight") # route for weight chart
def weightHistoryData(): # function to return weight history data for the logged-in user as JSON

# time period of a chart can be clicked by a button to change how the graph displays the data, zooming in and out

    period = request.args.get("period", "daily") # sets default period to daily of chart view
    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    
    if period == "daily": # if period is daily, executes following SQL query
        cursor.execute(
            "SELECT date, weight FROM bodyWeight WHERE userId = ? ORDER BY date ASC;",
            (session["userId"],),) # executes SQL query to get weight history data
        rows = cursor.fetchall() # fetches all rows from the database
        dataList = [] # creates an empty list to store the data
        for row in rows:
            dataList.append({"date": row["date"], "weight": row["weight"]}) # appends the data to the list
    elif period == "weekly": # if period is weekly, executes following SQL query
        cursor.execute(
            """
            SELECT date(MIN(date), 'weekday 0', '-6 days') as weekStart, AVG(weight) as avg_weight
            FROM bodyWeight
            WHERE userId = ?
            GROUP BY strftime('%Y-%W', date)
            ORDER BY weekStart ASC;
            """,
            (session["userId"],),) # executes SQL query to get weight history data on a weekly time view. uses aggregate SQL functions
        rows = cursor.fetchall() # fetches all rows from the database
        dataList = [] # creates an empty list to store the data
        for row in rows:
            dataList.append({"date": row["weekStart"], "weight": row["avg_weight"]}) # appends the data to the list
    elif period == "monthly": # if period is monthly, executes following SQL query
        cursor.execute(
            """
            SELECT strftime('%Y-%m', date) as month, AVG(weight) as avg_weight
            FROM bodyWeight
            WHERE userId = ?
            GROUP BY month
            ORDER BY month ASC;
            """,
            (session["userId"],),) # executes SQL query to get weight history data on a monthly time view
        rows = cursor.fetchall() # fetches all rows from the database
        dataList = [] # creates an empty list to store the data
        for row in rows:
            dataList.append({"date": row["month"], "weight": row["avg_weight"]}) # appends the data to the list
    else: # if period is yearly, executes following SQL query
        cursor.execute(
            """
            SELECT strftime('%Y', date) as year, AVG(weight) as avg_weight
            FROM bodyWeight
            WHERE userId = ?
            GROUP BY year
            ORDER BY year ASC;
            """,
            (session["userId"],),) # executes SQL query to get weight history data on a yearly time view
        rows = cursor.fetchall() # fetches all rows from the database
        dataList = [] # creates an empty list to store the data
        for row in rows:
            dataList.append({"date": row["year"], "weight": row["avg_weight"]}) # appends the data to the list
    
    return jsonify(dataList) # returns the data as JSON


@analytics_bp.route("/analytics/goals") # route for goal progress chart
def goalsProgress(): # function to return goal progress data for all user goals as JSON
    #used to show bar charts showing progress towards each goal
    
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    from ..models.goal import Goal # imports the Goal class from the goal model

    goalList = Goal.loadGoals(session["userId"]) # loads all goals for the user
    dataList = [] # creates an empty list to store the data

    for goal in goalList:
        progress = goal.calcProgress() # calculates the progress of the goal
        dataList.append({
            "goalID": goal.goalID,#assigns the goal ID to the data
            "description": goal.desc,  # goal description for the chart
            "targetValue": goal.targetValue,#assigns the target value to the data
            "currentValue": goal.currentValue,#assigns the current value to the data
            "progress_percent": progress,#assigns the progress percentage to the data
            "unit": goal.unit})#assigns the unit to the data

    return jsonify(dataList) # returns the data as JSON


def periodKey(date, period): # function to return the period label and sort key for grouping
    #date is in the format YYYY-MM-DD
    try:
        d = datetime.strptime(date[:10], "%Y-%m-%d") # parses the date string into a datetime object
    except (ValueError, TypeError): # if the date string is not valid, returns the date string
        return (date, date) # returns the date string
    if period == "daily": # if period is daily, returns the date string
        return (date[:10], date[:10]) # returns the date string
    if period == "weekly": # if period is weekly, returns the date string
        daysSinceSunday = (d.weekday() + 1) % 7 # calculates the number of days since Sunday to get the start of the week
        weekStart = d - timedelta(days=daysSinceSunday) # subtracts the number of days since Sunday to get the start of the week
        label = weekStart.strftime("%Y-%m-%d") # formats the date as YYYY-MM-DD for weekly
        return (label, label)
    if period == "monthly":
        label = d.strftime("%Y-%m") # formats the date as YYYY-MM for monthly
        return (label, label)
    if period == "yearly":
        label = d.strftime("%Y") # formats the date as YYYY for yearly
        return (label, label)
    return (date[:10], date[:10]) # returns the date string


@analytics_bp.route("/analytics/strength") # route for strength progression chart
def strengthProgression(): # function to return strength progression data for the logged-in user as JSON
    """
    Returns strength/cardio progression: gym = weight per rep, cardio = duration.
    Option to filter to one exercise; daily/weekly/monthly/yearly period for aggregation.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    exercise_filter = request.args.get("exercise", "").strip() # gets the exercise filter from the request
    period = request.args.get("period", "daily").lower() # gets the period from the request
    if period not in ("daily", "weekly", "monthly", "yearly"):
        period = "daily" # sets the period to daily as default
    db = g.db
    cursor = db.cursor()
    userId = session["userId"] # gets the user ID from the session

    cursor.execute(
        """
        SELECT e.exerciseName, e.exerciseType, el.date, el.weight, el.sets, el.reps, el.duration
        FROM exerciseLogs el
        JOIN exercises e ON el.exerciseId = e.exerciseId
        WHERE el.userId = ?
        ORDER BY e.exerciseName, el.date ASC;
        """,
        (userId,),) # executes SQL query to get strength progression data. uses cross-table parameterised SQL
    rows = cursor.fetchall() # fetches all rows from the database

    exerciseData = {} # creates an empty dictionary to store the exercise data
    for row in rows:
        name = row["exerciseName"] # gets the exercise name from the row
        if exercise_filter and name != exercise_filter: # if the exercise filter is set and the exercise name is not the same as the exercise filter, continue
            continue

        #here is the strength calculation i created and to be displayed on the chart

        etype = row["exerciseType"] or "gym" # gets the exercise type from the row
        if etype == "gym": # if the exercise type is gym, calculates the weight per rep
            w, s, r = row["weight"], row["sets"], row["reps"] # gets the weight, sets, and reps from the row
            reps_total = (s or 0) * (r or 0) # calculates the total number of reps
            y_value = (w / reps_total) if reps_total else (w or 0) # calculates the weight per rep
        else: # if the exercise type is cardio, gets the duration from the row
            y_value = row["duration"] or 0 # gets the duration from the row
        if name not in exerciseData: # if the exercise name is not in the exercise data, add it to the exercise data
            exerciseData[name] = {"exerciseType": etype, "dataPoints": []} # adds the exercise type and data points to the exercise data
        exerciseData[name]["dataPoints"].append({"date": row["date"], "yValue": y_value}) # adds the date and y value to the exercise data

    if period != "daily": # if the period is not daily, group the data by the period
        for name, data in exerciseData.items():
            buckets = {} # creates an empty dictionary to store the data by period (buckets)
            for i in data["dataPoints"]: # iterates through the data points
                label, sort_key = periodKey(i["date"], period) # gets the label and sort key for the data point
                if label not in buckets: # if the label is not in the buckets, add it to the buckets
                    buckets[label] = {"y_sum": 0, "n": 0, "sort_key": sort_key} # adds the label to the buckets
                buckets[label]["y_sum"] += i["yValue"] or 0 # adds the y value to the buckets
                buckets[label]["n"] += 1 # adds the n to the buckets
            data["dataPoints"] = [ # iterates through the buckets
                {"date": label, "yValue": round(b["y_sum"] / b["n"], 1) if b["n"] else 0} # adds the date and y value to the data points
                for label, b in sorted(buckets.items(), key=lambda x: x[1]["sort_key"]) # sorts the buckets by the sort key
            ]

    resultList = [
        {"exerciseName": name, "exerciseType": data["exerciseType"], "dataPoints": data["dataPoints"]}
        for name, data in exerciseData.items()] # adds the exercise name and exercise type and data points to the result list
    return jsonify(resultList)


@analytics_bp.route("/analytics/nutrients") # route for nutrient intake chart
def nutrient_intake(): # function to return nutrient intake data for the logged-in user as JSON
    """
    Returns nutrient intake data (calories and protein) over time
    Used to create line charts showing daily intake.
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    db = g.db
    cursor = db.cursor()

    # Get all diet logs grouped by date.
    cursor.execute(
        """
        SELECT date, SUM(calories) as total_calories, SUM(protein) as total_protein
        FROM dietLogs
        WHERE userId = ?
        GROUP BY date
        ORDER BY date ASC;
        """,
        (session["userId"],)
    )# executes SQL query to get nutrient intake data
    rows = cursor.fetchall() # fetches all rows from the database
    dataList = [] # creates an empty list to store the data
    for row in rows: # iterates through the rows
        dataList.append({"date": row["date"], "calories": row["total_calories"] or 0, "protein": row["total_protein"] or 0}) 
        # adds the date, calories, and protein to the data list
    return jsonify(dataList) # returns the data as JSON


@analytics_bp.route("/analytics/calories") # route for calories intake chart
def calories_intake(): # function to return calories intake data for the logged-in user as JSON
    """
    Returns calories spent (exercise), gained (diet), and net (gained - spent) in a period of time
    Used to create line charts showing daily intake
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    period = request.args.get("period", "weekly") # gets the time period clicked by the user from the request
    db = g.db
    cursor = db.cursor()
    userId = session["userId"] # gets the user ID from the session

    if period == "daily": # if the period is daily, executes following SQL query
        cursor.execute(
            """
            SELECT date, COALESCE(SUM(caloriesBurned), 0) FROM exerciseLogs WHERE userId = ? GROUP BY date;
            """,
            (userId,),
        )# executes SQL query to get calories spent data
        spent_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database   
        cursor.execute(
            """
            SELECT date, COALESCE(SUM(calories), 0) FROM dietLogs WHERE userId = ? GROUP BY date;
            """,# executes SQL query to get calories gained data
            (userId,),)
        gained_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database
        all_dates = sorted(set(spent_by) | set(gained_by)) # sorts the dates
        dataList = [ # creates an empty list to store the data
            {"period": d, "spent": spent_by.get(d, 0), "gained": gained_by.get(d, 0), "net": gained_by.get(d, 0) - spent_by.get(d, 0)} # adds the date, calories spent, calories gained, and net calories to the data list
            for d in all_dates] # iterates through the dates
    elif period == "weekly": # if the period is weekly, executes following SQL query
        cursor.execute(
            """
            SELECT date(date, 'weekday 0', '-6 days') as p, COALESCE(SUM(caloriesBurned), 0) FROM exerciseLogs WHERE userId = ? GROUP BY strftime('%Y-%W', date) ORDER BY p;
            """,
            (userId,),)# executes SQL query to get calories spent data
        spent_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database
        cursor.execute(
            """
            SELECT date(date, 'weekday 0', '-6 days') as p, COALESCE(SUM(calories), 0) FROM dietLogs WHERE userId = ? GROUP BY strftime('%Y-%W', date) ORDER BY p;
            """,
            (userId,),)# executes SQL query to get calories gained data
        gained_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database
        all_periods = sorted(set(spent_by) | set(gained_by))# sorts the periods
        dataList = [
            {"period": p, "spent": spent_by.get(p, 0), "gained": gained_by.get(p, 0), "net": gained_by.get(p, 0) - spent_by.get(p, 0)}
            for p in all_periods] # iterates through the periods and adds the period, calories spent, calories gained, and net calories to the data list
    elif period == "monthly": # if the period is monthly, executes following SQL query
        cursor.execute(
            """
            SELECT strftime('%Y-%m', date) as p, COALESCE(SUM(caloriesBurned), 0) FROM exerciseLogs WHERE userId = ? GROUP BY p;
            """,
            (userId,),)# executes SQL query to get calories spent data
        spent_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database
        cursor.execute(
            """
            SELECT strftime('%Y-%m', date) as p, COALESCE(SUM(calories), 0) FROM dietLogs WHERE userId = ? GROUP BY p;
            """,
            (userId,),
        )# executes SQL query to get calories gained data
        gained_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database
        all_periods = sorted(set(spent_by) | set(gained_by))# sorts the periods
        dataList = [
            {"period": p, "spent": spent_by.get(p, 0), "gained": gained_by.get(p, 0), "net": gained_by.get(p, 0) - spent_by.get(p, 0)}
            for p in all_periods] # iterates through the periods and adds the period, calories spent, calories gained, and net calories to the data list
    else:  # yearly
        cursor.execute(
            """
            SELECT strftime('%Y', date) as p, COALESCE(SUM(caloriesBurned), 0) FROM exerciseLogs WHERE userId = ? GROUP BY p;
            """,
            (userId,),
        ) # executes SQL query to get calories gained data
        spent_by = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute(
            """
            SELECT strftime('%Y', date) as p, COALESCE(SUM(calories), 0) FROM dietLogs WHERE userId = ? GROUP BY p;
            """,
            (userId,),
        ) # executes SQL query to get calories spent data
        gained_by = {row[0]: row[1] for row in cursor.fetchall()} # fetches all rows from the database
        all_periods = sorted(set(spent_by) | set(gained_by))# sorts the periods
        dataList = [
            {"period": p, "spent": spent_by.get(p, 0), "gained": gained_by.get(p, 0), "net": gained_by.get(p, 0) - spent_by.get(p, 0)}
            for p in all_periods] # iterates through the periods and adds the period, calories spent, calories gained, and net calories to the data list
        

    return jsonify(dataList) # returns the data as JSON


@analytics_bp.route("/analytics/protein") # route for protein intake chart
def protein_intake(): # function to return protein intake data for the logged-in user as JSON
    """
    Returns protein intake data over time
    Used to create line charts showing daily intake
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page

    period = request.args.get("period", "weekly") # gets the time period clicked by the user from the request
    db = g.db
    cursor = db.cursor() # gets the database cursor

    if period == "daily": # if the period is daily, executes following SQL query
        cursor.execute(
            """
            SELECT date, SUM(protein) as total_protein
            FROM dietLogs
            WHERE userId = ?
            GROUP BY date
            ORDER BY date ASC;
            """,
            (session["userId"],)
        )# executes SQL query to get protein intake data    
    elif period == "weekly": # if the period is weekly, executes following SQL query
        cursor.execute(
            """
            SELECT strftime('%Y-W%W', date) as period, SUM(protein) as total_protein
            FROM dietLogs
            WHERE userId = ?
            GROUP BY period
            ORDER BY period ASC;
            """,
            (session["userId"],)
        )# executes SQL query to get protein intake data
    elif period == "monthly":
        cursor.execute(
            """
            SELECT strftime('%Y-%m', date) as period, SUM(protein) as total_protein
            FROM dietLogs
            WHERE userId = ?
            GROUP BY period
            ORDER BY period ASC;
            """,
            (session["userId"],)
        )# executes SQL query to get protein intake data
    else:  # yearly
        cursor.execute(
            """
            SELECT strftime('%Y', date) as period, SUM(protein) as total_protein
            FROM dietLogs
            WHERE userId = ?
            GROUP BY period
            ORDER BY period ASC;
            """,
            (session["userId"],)
        )
    # executes SQL query to get protein intake data 
    rows = cursor.fetchall()
    dataList = [] # creates an empty list to store the data
    for row in rows: # iterates through the rows
        dataList.append({"period": row[0], "protein": row[1] or 0}) # adds the period and protein to the data list
    return jsonify(dataList) # returns the data as JSON



