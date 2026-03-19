# entry point iniitiating flask app and runs the development server in debug mode (a server that runs the app and allows me to see the changes you make to the code in real time without having to restart the server)
# this is useful for me to debu and make changes to my prgram as i create it
from flask import Flask
from app import create_app


def create_app_wrapper(): # function to create the Flask app so this file can be run directly
    """
    a wrapper for running this file directly, starting the Flask app and also keeps the entry point readable.
    """
    app = create_app() # gets the app from the app package
    return app # returns the app instance


app = create_app_wrapper() # creates the app when this module is loaded


if __name__ == "__main__":
    app.run(debug=True) # starts the development server when you run python main.py