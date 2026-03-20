# nutrition helper: uses FatSecret API for up to date calories and protein content in food 

from flask import g
from .fatsecret_api import getFoodMacro


def calcNutrients(foodName, mass): # function to get calories and protein for a food and mass
    """
    calculates nutrients for a given food name and mass in grams found from fatsecret api service and user input

    1. calls the FatSecret API helper to get data
    2. ensures the local nutritionDatabase table exists and caches the result (carbs/fats stored as 0.0)
    3. returns a dictionary with foodName, calories and protein
    """
    apiResult = getFoodMacro(foodName, mass) # gets data from the FatSecret API

    if apiResult is None:
        return None # returns None if the API found no results

    db = g.db # gets the database connection
    cursor = db.cursor() # gets the database cursor
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nutritionDatabase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foodName TEXT UNIQUE,
            caloriesPer100g REAL,
            proteinPer100g REAL
        );
        """
    ) # executes SQL to ensure the nutrition table exists

# the format of api call is semi structured data with no clear per 100g values so we calculate it here with the values they do provide
    caloriesPer100 = (apiResult["calories"] / mass) * 100.0 # finds calories in the food and converts to per 100g for storage
    proteinPer100 = (apiResult["protein"] / mass) * 100.0 # 

    cursor.execute(
        """
        INSERT OR IGNORE INTO nutritionDatabase (foodName, caloriesPer100g, proteinPer100g)
        VALUES (?, ?, ?);
        """,
        (apiResult["foodName"], caloriesPer100, proteinPer100),
    ) # executes SQL query to cache the food in the local table
    db.commit() # saves the changes to the database

    return apiResult # returns the API result (foodName, calories, protein)

