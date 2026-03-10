# entry point to run the fitness tracker Flask app (python main.py starts the development server)

from flask import Flask
from app import create_app


def create_app_wrapper(): # function to create the Flask app so this file can be run directly
    """
    simple wrapper so running this file directly will start the Flask app. keeps the entry point readable.
    """
    app = create_app() # gets the app from the app package
    return app # returns the app instance


app = create_app_wrapper() # creates the app when this module is loaded


if __name__ == "__main__":
    app.run(debug=True) # when you run python main.py, starts the development server; debug=True reloads on code change
