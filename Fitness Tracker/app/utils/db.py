# database connection, table creation
#file used to first create the fitness_tracker.db database and insert default data
# uses complex data model in database like several interlinked tables

import os
import sqlite3
from datetime import datetime


def connect(db_path): # function to create a connection to the SQLite database
    """
    creates a connection to the SQLite database. if the database file does not exist yet, SQLite will create it.
    """
    db_dir = os.path.dirname(db_path) # gets the directory of the database file
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True) # ensures the database directory exists

    conn = sqlite3.connect(db_path, check_same_thread=False) # check_same_thread=False lets us reuse the connection in Flask
    conn.row_factory = sqlite3.Row # allows access to columns by name, e.g. row['username']
    return conn # returns the connection


def createTables(conn): # function to create the main tables if they do not already exist
    """
    """
    cursor = conn.cursor() # gets the database cursor

    # users table: stores login information (with hashed passwords). uses complex data model in database
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            userId INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            passwordHash TEXT,
            createdAt TEXT
        );
        """
    ) # executes SQL query to create the users table

    # exercises table: list of exercises with their MET values
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exercises (
            exerciseId INTEGER PRIMARY KEY AUTOINCREMENT,
            exerciseName TEXT UNIQUE,
            exerciseType TEXT,
            metValue REAL
        );
        """
    ) # executes SQL query to create the exercises table

    # exercise logs: each row is one exercise session
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exerciseLogs (
            logId INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER,
            exerciseId INTEGER,
            date TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            duration REAL,
            caloriesBurned REAL,
            FOREIGN KEY (userId) REFERENCES users(userId),
            FOREIGN KEY (exerciseId) REFERENCES exercises(exerciseId)
        );
        """
    ) # uses cross-table parameterised SQL via foreign keys

    # diet logs: each row is one food entry with calories and protein
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dietLogs (
            logId INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER,
            foodName TEXT,
            date TEXT,
            mass REAL,
            calories REAL,
            protein REAL,
            FOREIGN KEY (userId) REFERENCES users(userId)
        );
        """
    ) # executes SQL query to create the diet logs table

    # workout presets: allow users to save a group of exercises
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workoutPresets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER,
            presetName TEXT,
            exercisesJson TEXT,
            createdAt TEXT,
            updatedAt TEXT,
            FOREIGN KEY (userId) REFERENCES users(userId)
        );
        """
    ) # executes SQL query to create the workout presets table

    # goals table: stores different types of user goals
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER,
            goalType TEXT,
            targetValue REAL,
            targetDate TEXT,
            currentValue REAL,
            unit TEXT,
            description TEXT,
            createdAt TEXT,
            FOREIGN KEY (userId) REFERENCES users(userId)
        );
        """
    ) # executes SQL query to create the goals table

    # body weight logs: simple optional table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bodyWeight (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER,
            weight REAL,
            date TEXT,
            createdAt TEXT,
            FOREIGN KEY (userId) REFERENCES users(userId)
        );
        """
    ) # executes SQL query to create the body weight logs table

    # nutrition database: optional local cache for food nutrition data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nutritionDatabase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foodName TEXT UNIQUE,
            caloriesPer100g REAL,
            proteinPer100g REAL,
            carbsPer100g REAL,
            fatsPer100g REAL
        );
        """
    ) # executes SQL query to create the nutrition database table

    # tips table: stores science-based fitness and diet tips
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            content TEXT,
            source TEXT
        );
        """
    ) # executes SQL query to create the tips table

    conn.commit() # saves the changes to the database


def defaultExercise(conn): # function to insert default exercises with MET values
    """
    inserts some default exercises with MET values. uses INSERT OR IGNORE so running multiple times will not duplicate rows.
    """
    cursor = conn.cursor() # gets the database cursor

    default_exercises = [
        ("Walking (slow)", "cardio", 3.0),
        ("Walking (brisk)", "cardio", 4.3),
        ("Running (8 km/h)", "cardio", 8.3),
        ("Running (10 km/h)", "cardio", 10.0),
        ("Cycling (leisure)", "cardio", 4.0),
        ("Cycling (fast)", "cardio", 8.5),
        ("Bicep curls", "gym", 3.0),
        ("Bench press", "gym", 6.0),
        ("Squats", "gym", 5.0),
        ("Deadlift", "gym", 6.0),] # creates a list of default exercises with their name, type and MET value

    for exerciseName, exerciseType, metValue in default_exercises:
        cursor.execute(
            """
            INSERT OR IGNORE INTO exercises (exerciseName, exerciseType, metValue)
            VALUES (?, ?, ?);
            """,
            (exerciseName, exerciseType, metValue),
        ) # executes SQL query to insert the exercise

    conn.commit() # saves the changes to the database


def tips(conn): # function to insert default science based tips into the tips table
    """
    inserts some default science based tips into the tips table. simple examples for the app.
    """
    cursor = conn.cursor() # gets the database cursor

    default_tips = [
        ("exercise", "Progressive Overload", "Gradually increase the weight, reps, or sets over time to continue making progress. This is the key principle behind strength training.", "Exercise Science Basics"),
        ("exercise", "Rest Days Are Important", "Your muscles need time to recover and grow. Aim for at least one rest day between intense workouts for the same muscle group.", "Recovery Science"),
        ("diet", "Protein for Muscle Growth", "Aim for 1.6-2.2g of protein per kg of body weight daily if you're trying to build muscle. Spread it across meals throughout the day.", "Nutrition Research"),
        ("diet", "Stay Hydrated", "Drink water throughout the day, especially around workouts. Dehydration can significantly impact performance and recovery.", "Sports Nutrition Guidelines"),
        ("exercise", "Warm Up Before Exercise", "A proper warm-up increases blood flow to muscles and reduces injury risk. Start with 5-10 minutes of light cardio.", "Injury Prevention Studies"),
        ("diet", "Eat Whole Foods", "Focus on whole, unprocessed foods like vegetables, fruits, lean proteins, and whole grains for better nutrition and satiety.", "Nutrition Science"),
        ("diet", "Creatine: Dose and Benefits", "A dose of 3-5 g per day is effective for most people; some use a loading phase of about 20 g/day for 5-7 days then 3-5 g for maintenance. Benefits include improved strength and power, support for muscle mass and recovery, and some evidence for cognitive benefits. It is one of the most researched supplements in sport nutrition.", "Sports Nutrition Research"),
        ("exercise", "Emphasise the Eccentric", "The eccentric (lowering) phase of a lift—e.g. slowly lowering the bar in a bench press—produces more force and muscle tension than the concentric phase. Emphasising controlled eccentrics can improve strength, muscle growth and tendon adaptation, and may reduce injury risk by building resilience under load.", "Strength and Conditioning Research"),]
        # creates a list of default tips with their category, title, content and source

    for category, title, content, source in default_tips:
        cursor.execute(
            """
            INSERT OR IGNORE INTO tips (category, title, content, source)
            VALUES (?, ?, ?, ?);
            """,
            (category, title, content, source),
        ) # executes SQL query to insert the tip

    conn.commit() # saves the changes to the database


def currentTime(): # function to return the current time as a string
    """
    returns the current time as a simple string. useful for createdAt and date fields.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

