"""
Workout preset models

Classes for saved workout templates (e.g. "Push Day", "Leg Day"). Each preset has a name and a list of exercises; 
each exercise stores name, and either sets/reps/weight (gym) or duration (cardio). 
Presets are saved to the workoutPresets table and loaded back when the user opens the Workouts page or chooses a preset to log
and logged workouts can be modified without changing the original preset as a new preset instance

uses OOP classes and composition, hash tables, parsing JSON
"""
import json
from flask import g
from ..utils.data_structures import Stack


class ExercisePreset: # uses OOP model i created
    """
    This class represents one exercise inside a preset.
    e.g:
    For gym exercises: Bench press, 3 sets of 8 reps at 60 kg
    For cardio exercises: Running, 30 minutes
    """

    def __init__(self, exerciseName, setsValue=None, repsValue=None, weightValue=None, durationValue=None):
        self.exerciseName = exerciseName
        self.setsValue = setsValue
        self.repsValue = repsValue
        self.weightValue = weightValue
        self.durationValue = durationValue

    def toDict(self):
        """
        Converts object into a dictionary.
        useful for saving to the database as JSON.
        """
        result = {"exerciseName": self.exerciseName} # creates a dictionary with the exercise name
        # Includes gym fields if it is not None and therefor is a gym exercise
        if self.setsValue != None:
            result["sets"] = self.setsValue # adds sets to result dictionary
        if self.repsValue != None:
            result["reps"] = self.repsValue # adds reps to result dictionary
        if self.weightValue != None:
            result["weight"] = self.weightValue # adds weight to result dictionary
        # includes cardio field if it is not None and therefor is a cardio exercise
        if self.durationValue != None:
            result["duration"] = self.durationValue # adds duration to result dictionary
        return result


class WorkoutPreset: # uses OOP model i created
    """
    A workout preset is a list of preset exercises with a name like:
    Push Day or Leg Day
    """

    def __init__(self, presetName, exerciseList=None, presetId=None): # initializes the workout preset with a name and a list of exercise presets
        self.presetName = presetName # sets the name of the workout preset
        self.exerciseList = Stack() # uses Stack (LIFO) so we can push exercises and pop for undo
        if exerciseList is not None:
            for ex in exerciseList:
                self.exerciseList.push(ex) # load existing exercises onto the stack

    def add_exercise(self, exercisePreset): # adds a new exercise preset to the workout preset
        self.exerciseList.push(exercisePreset) # uses Stack Operations (push) from data_structures.py

    def remove_last_exercise(self):
        """
        stack-like behaviour removing the last exercise (pop off the stack, LIFO ) that was added
        like an undo for the user when they add the wrong exercise
        """
        if not self.exerciseList.is_empty():
            self.exerciseList.pop() # uses Stack Operations (pop) from data_structures.py; removes the last exercise added   

    def to_json_string(self): # converts the list of exercise presets to a JSON string so it can be stored in the database
        dataList = [] # creates a list to store the exercise presets
        for ex in self.exerciseList: # loops through the exercise list. uses list operations
            dataList.append(ex.toDict()) # adds the exercise preset to the data list
        return json.dumps(dataList) # returns the data list as a JSON string

    def savetoDB(self, userId):
        """
        Saves the workout preset into the workoutPresets table.
        if presetId is set, row is updated; otherwise new row is inserted
        """
        db = g.db
        cursor = db.cursor()
        exercisesJson = self.to_json_string() # converts the list of exercise presets to a JSON string so it can be stored in the database

        if self.presetId is None: # if the preset id is not set, a new row is inserted
            cursor.execute(
                """
                INSERT INTO workoutPresets (userId, presetName, exercisesJson, createdAt, updatedAt)
                VALUES (?, ?, ?, datetime('now'), datetime('now'));
                """,
                (userId, self.presetName, exercisesJson),) # inserts the user id, preset name, and exercises JSON into the database
            db.commit()
            self.presetId = cursor.lastrowid # sets the preset id to the last row id inserted into the database
        else:
            cursor.execute(
                """
                UPDATE workoutPresets
                SET presetName = ?, exercisesJson = ?, updatedAt = datetime('now')
                WHERE id = ?;
                """,
                (self.presetName, exercisesJson, self.presetId),) # updates the preset name, exercises JSON, and updated at to the current date and time
            db.commit()

    @staticmethod# allows the method can be called on the class itself without creating an instance of the class
    def loadFromDB(preset_id):
        """
        Loads the workout preset from the database by the preset id.
        """
        db = g.db
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM workoutPresets WHERE id = ?;", #sql statement for selecting the workout preset from the database by the preset id
            (preset_id,),) # the preset id used as the parameter for the sql statement
        row = cursor.fetchone()
        if row is None:
            return None

        # This row is one record from the workoutPresets table (we just selected it by preset_id).
        # The exercisesJson column was filled when the user saved the preset on the Workouts page
        # (e.g. /exercise/workouts): they add exercises, click save, and savetoDB() writes that JSON here.
        exercisesJson = row["exercisesJson"]
        exerciseDicts = json.loads(exercisesJson)  # list of dicts, one per exercise. uses parsing JSON (from DB column)

        exerciseList = [] # uses list operations
        for item in exerciseDicts:
            name = item.get("exerciseName") 
            # checks if it's a cardio exercise (has duration) or gym exercise (has sets/reps/weight)
            if "duration" in item and item.get("duration") != None:
                ex = ExercisePreset(name,setsValue=None,repsValue=None,weightValue=None,durationValue=item.get("duration"))
                # creates new preset with correct values for a cardio exercise
            else:
                ex = ExercisePreset(name,setsValue=item.get("sets"),repsValue=item.get("reps"),weightValue=item.get("weight"),durationValue=None)
                # creates new preset with correct values for a gym exercise
            exerciseList.append(ex)
        return WorkoutPreset(row["presetName"], exerciseList, presetId=row["id"]) # uses composition (WorkoutPreset contains list of ExercisePreset)


class PresetInstance: # uses OOP model i created
    """
    A modified instance of a workout preset.
    
    This uses OOP composition: a PresetInstance "has a" WorkoutPreset,
    but can modify exercises for just this one workout session without
    changing the original preset in the database
    """

    def __init__(self, basePreset): # base preset or workout created by the user entered as a parameter
        """
        Create an instance from created base preset by the user
        making a copy of the exerciseList so it can be modified without changing the original preset
        uses encapsulation to protect the original preset from being modified 
        and composition to create a new instance of the preset
        """
        self.basePreset = basePreset # uses composition (PresetInstance has a WorkoutPreset)
        self.exerciseList = [] # creates a list to store the exercise presets. uses list operations
        # copies exercises from the base preset to the exercise list so it can be modified without changing the original preset
        for i in basePreset.exerciseList: # loops through the exercise list of the base preset
            self.exerciseList.append(ExercisePreset(
                i.exerciseName,setsValue=i.setsValue,repsValue=i.repsValue,weightValue=i.weightValue,durationValue=i.durationValue))
                # creates new exercise preset with the same values as the exercise in the base preset

    def modifyExercise(self, exerciseIndex, newSets=None, newReps=None, newWeight=None):
        """
        Modifies an exercise in this instance.
        This only changes this instance, not the original preset
        
        """
        if exerciseIndex < 0 or exerciseIndex >= len(self.exerciseList): # checks if the exercise index is valid
            return False

        ex = self.exerciseList[exerciseIndex] # gets the exercise from the exercise list
        if newSets != None:
            ex.setsValue = newSets # sets the sets value of the exercise
        if newReps != None:
            ex.repsValue = newReps # sets the reps value of the exercise
        if newWeight != None:
            ex.weightValue = newWeight # sets the weight value of the exercise

        return True

    def createNewInstance(self):
      #  creates a new instance from this instance (for chaining or copying).
        newPreset = WorkoutPreset(self.basePreset.presetName, self.exerciseList.copy())
        return PresetInstance(newPreset)

    def toDict(self):
       # converts the instance to a dictionary so it can be used in templates
        
        return {
            "presetName": self.basePreset.presetName,
            "exercises": [ex.toDict() for ex in self.exerciseList]} # returns the preset name and the exercises as a dictionary

