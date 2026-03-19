from flask import Flask, g
import os
from .utils.db import connect, createTables, defaultExercise, tips


def create_app():
    """
    Creates the Flask app, sets basic configuration and prepares the database
   
    """
    # calculates the base directory (the root directory of the project)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))# gets the directory of the file
    static_folder = os.path.join(base_dir, "static") # this is the folder that contains the static files like css, js, images, etc.
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates") # this is the folder that contains the template files like html, jinja2, etc.

    # creates the Flask app with explicit static and template folder paths
    # this ensures Flask finds the static files in the directory
    app = Flask(__name__, 
                static_folder=static_folder,
                static_url_path="/static",
                template_folder=template_folder) # creates the Flask app with the static and template folder paths

    # im creating a secret key needed for sessions - login system - to encrypt the session data for security
    app.config["SECRET_KEY"] = "FittyFitFit" # secret key
    # path to the SQLite database file in database folder
    db_path = os.path.join(base_dir, "database", "fitness_tracker.db") # joins the base directory and the database folder and the database file
    app.config["DATABASE_PATH"] = db_path # sets the database path to the database file

    # makes sure and verifies the database and tables exist on startup in case of any errors or missing tables
    with app.app_context():# provides Flask application its configuration for the current request
        conn = connect(app.config["DATABASE_PATH"]) # connects to the database
        if conn is not None: # if the connection is not None
            createTables(conn) # creates the tables
            defaultExercise(conn) # inserts the default exercises
            tips(conn) # inserts the tips
            conn.close() # closes the connection

    @app.before_request
    def load_db():
        """
        opens a database connection for each request and stores it in `g`
        avoids passing the connection around in each route
        """
        if "db" not in g:
            g.db = connect(app.config["DATABASE_PATH"]) # connects to the database

    @app.teardown_appcontext
    def close_db(exception):
        """
        closes the database connection when the request is finished
        """
        db = g.pop("db", None) # pops the database connection from the global object g
        if db is not None: # if the database connection is not None
            db.close() # closes the database connection

    # registers blueprints (the route modules for each page)
    from .routes.auth import auth_bp
    from .routes.exercise import exercise_bp
    from .routes.diet import diet_bp
    from .routes.dashboard import dashboard_bp
    from .routes.goals import goals_bp
    from .routes.analytics import analytics_bp
    from .routes.tips import tips_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(diet_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(tips_bp)

    return app

