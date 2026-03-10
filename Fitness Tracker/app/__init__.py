from flask import Flask, g
import os
from .utils.db import connect, createTables, defaultExercise, tips


def create_app():
    """
    App factory function.
    This creates the Flask app, sets basic configuration,
    and prepares the database. Kept simple and readable.
    """
    # Calculate the base directory (project root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder = os.path.join(base_dir, "static")
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

    # Create Flask app with explicit static and template folder paths
    # This ensures Flask finds static files in the root-level static/ directory
    app = Flask(__name__, 
                static_folder=static_folder,
                static_url_path="/static",
                template_folder=template_folder)

    # Secret key is needed for sessions (login).
    # In a real project you would load this from an environment variable.
    app.config["SECRET_KEY"] = "change_this_in_production"

    # Path to the SQLite database file (in the local 'database' folder).
    db_path = os.path.join(base_dir, "database", "fitness_tracker.db")
    app.config["DATABASE_PATH"] = db_path

    # Make sure database and tables exist on startup.
    # Note: In Flask 3.0+, before_first_request is deprecated.
    # We initialize the database when the app is created instead.
    with app.app_context():
        conn = connect(app.config["DATABASE_PATH"])
        if conn is not None:
            createTables(conn)
            defaultExercise(conn)
            tips(conn)
            conn.close()

    @app.before_request
    def load_db():
        """
        Open a database connection for each request and store it in `g`.
        This keeps things simple and avoids passing the connection around.
        """
        if "db" not in g:
            g.db = connect(app.config["DATABASE_PATH"])

    @app.teardown_appcontext
    def close_db(exception):
        """
        Close the database connection when the request is finished.
        """
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # Register blueprints (route modules).
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

