# Goal and body weight models.
# uses OOP and list operations, dynamic generation of objects from database rows

from flask import g # imports g to use the global object so so I can store a database connection in it that my code refreshes on every request


class Goal:
    """
    Goal class represents a user goal they set.
   e.g:
    - Bench press 100 kg by 21st Jan
    - Reach 70 kg body weight by 2027
    """

    def __init__(self, goalType, targetValue, targetDate, unit, desc, goalID = None, currentValue = 0):
        self.goalType = goalType # creating goal type attribute
        self.targetValue = targetValue # creating target value attribute
        self.targetDate = targetDate # creating target date attribute
        self.unit = unit # creating unit attribute
        self.desc = desc # creating description attribute
        self.goalID = goalID # creating goal ID attribute
        self.currentValue = currentValue # creating current value attribute

    def calcProgress(self):
        """
        a simple progress calculation assuming:
        - For things like protein or strength, we compare currentValue to targetValue.
        - Progress is displayed as percentage, limited at 100%.
        """
        if self.targetValue == 0:
            return 0 
        else:
            percentage = (self.currentValue / self.targetValue) * 100 # calculates the progress as a percentage
            return round(percentage, 1) # returns rounded percentage to 1 decimal place

    def saveToDB(self, userId):
        """
        saves the instance of goal into the goals table
        if goalID is None then inserts a new goal row
        otherwise updates the existing row
        """
        db = g.db # accesses the database using the global object g
        cursor = db.cursor() # creates a cursor object to execute SQL commands
        if self.goalID is None:
            cursor.execute(
                """
                INSERT INTO goals (userId, goalType, targetValue, targetDate, currentValue, unit, description, createdAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'));
            """, (userId, self.goalType, self.targetValue, self.targetDate, self.currentValue, self.unit, self.desc))
            #creates a new goal row in the database with the relevant values
            db.commit() # inserts relevant values for goal into the database
            self.goalID = cursor.lastrowid # sets the goalID to the last row id inserted into the database
        else:
            #updates the existing goal row in the database with the relevant values
            cursor.execute(
                """
                UPDATE goals
                SET goalType = ?, targetValue = ?, targetDate = ?, currentValue = ?, unit = ?, description = ?
                WHERE id = ?;
            """, (self.goalType, self.targetValue, self.targetDate, self.currentValue, self.unit, self.desc, self.goalID))
            db.commit() # updates the database with the new values for the goal

    @staticmethod
    def loadGoals(userId):
        """
        Load all goals for a specific user and return them as a list of Goal objects.
        """
        db = g.db # accesses the database using the global object g here same as above
        cursor = db.cursor()
        cursor.execute("SELECT * FROM goals WHERE userId = ? ORDER BY createdAt DESC;", (userId,)) # executes the SQL command to select all goals for the user and order them by the createdAt column in descending order
        rows = cursor.fetchall() # fetches all the rows from the database
        goalList = [] # creates an empty list to store the goals
        for row in rows:
            gObject = Goal( # creates a new Goal object for each row
                row["goalType"], # assigns the goal type to the goal object
                row["targetValue"], # assigns the target value to the goal object   
                row["targetDate"], # assigns the target date to the goal object
                row["unit"], # assigns the unit to the goal object
                row["description"], # assigns the description to the goal object
                goalID=row["id"], # assigns the goal ID to the goal object
                currentValue=row["currentValue"], # assigns the current value to the goal object
            ) # uses dynamic generation of objects based on OOP model
            goalList.append(gObject) # adds the goal object to the list. uses list operations
        return goalList # returns the list of goal objects

