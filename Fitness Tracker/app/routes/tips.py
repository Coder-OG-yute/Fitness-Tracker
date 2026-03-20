# routes for tips page, random tip and search by keyword or category

from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, g
import random
from ..utils.data_structures import Queue


# blueprint for tips page and tips API endpoints
tips_bp = Blueprint("tips", __name__)


@tips_bp.route("/tips", endpoint="tips_page") # route for tips page
def tips_page(): # function to render the tips page
    """
    main tips page that displays tips and allows searching
    """
    if "userId" not in session: # if user is not logged in, redirect to login page
        return redirect(url_for("auth.login")) # redirect to login page
    return render_template("tips.html") # renders the tips template


@tips_bp.route("/tips/random") # route for a random tip as JSON
def random_tip(): # function to return a random tip from the database as JSON
    """
    returns a random tip from the database
    selects all tips then uses random.choice to pick one.
    """
    if "userId" not in session: # if user is not logged in, return error
        return jsonify({"error": "Not logged in"}), 401

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT category, title, content, source FROM tips ORDER BY title;"
    ) # executes SQL query to get all tips
    allTips = cursor.fetchall() # fetches all rows from the database

    if len(allTips) == 0:
        return jsonify({
            "category": "general",
            "title": "No tips available",
            "content": "Tips will be added soon.",
            "source": "System"
        }) # returns a default message if no tips exist

    randomTip = random.choice(allTips) # picks a random tip from the list

    tip = {
        "category": randomTip["category"],
        "title": randomTip["title"],
        "content": randomTip["content"],
        "source": randomTip["source"]
    } # builds the tip dict for the JSON response
    return jsonify(tip) # returns the tip as JSON


@tips_bp.route("/tips/search") # route for searching tips by keyword
def search_tips(): # function to return tips matching the keyword as JSON
    """
    searches tips by keyword in title or content
    uses SQL LIKE with % to match any text containing the keyword
    """
    if "userId" not in session: # if user is not logged in, return error
        return jsonify({"error": "Not logged in"}), 401 # returns error message if user is not logged in

    keyword = request.args.get("keyword", "").strip() # gets the keyword from the request

    if not keyword:
        return jsonify({"error": "Please provide a keyword"}), 400 # returns error message if no keyword is provided

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor

    cursor.execute(
        """
        SELECT category, title, content, source
        FROM tips
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY title;
        """,
        (f"%{keyword}%", f"%{keyword}%")
    ) # executes SQL query to search tips by keyword in title or content
    results = cursor.fetchall() # fetches all rows from the database
    tipsList = [] # creates an empty list to store the tips
    # Queue used (FIFO): process results in order via enqueue/dequeue
    q = Queue()
    for row in results: # enqueues each row into the queue to process in order
        q.enqueue(row)
    while not q.is_empty(): # dequeues each row from the queue to build the tips list
        row = q.dequeue() # dequeues the next row from the queue
        tipsList.append({
            "category": row["category"],
            "title": row["title"],
            "content": row["content"],
            "source": row["source"]
        })

    return jsonify(tipsList) # returns the tips list as JSON


@tips_bp.route("/tips/category/<category>") # route for filtering tips by category
def tipsCat(category): # function to return tips in the category passed in parameter as JSON
    """
    filters tips by category (diet/exercise)
    returns matching tips as JSON
    """
    if "userId" not in session: # if user is not logged in, return error
        return jsonify({"error": "Not logged in"}), 401 # returns error message if user is not logged in

    if category not in ["diet", "exercise"]: # only allow diet or exercise categories
        return jsonify({"error": "Invalid category. Use 'diet' or 'exercise'"}), 400 # returns error message if category is not valid

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        "SELECT category, title, content, source FROM tips WHERE category = ? ORDER BY title;",
        (category,)
    ) # executes SQL query to get tips in the given category
    results = cursor.fetchall() # fetches all rows from the database
    tipsList = [] # creates an empty list to store the tips

    for row in results:
        tipsList.append({
            "category": row["category"],
            "title": row["title"],
            "content": row["content"],
            "source": row["source"]
        }) # appends each row as a dict to the list

    return jsonify(tipsList) # returns the tips list as JSON
