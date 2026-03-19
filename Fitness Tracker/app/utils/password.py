# password validation: checks strength and returns list of errors

import re


def valPass(password): # function to check if a password meets strength rules
    """
    checks if the password is strong enough by set criteria i set

    returns  isValid (True if passes all checks otherwise False) 
    and errorList (list of string text explaining what is wrong).
    """
    errorList = [] # creates an empty list to store error messages

    if len(password) < 8: # rule 1: at least 8 characters long
        errorList.append("Password must be at least 8 characters long.")

    if not re.search(r"[a-z]", password): # rule 2: at least one lowercase letter (searches string input for lowercase letters)
        errorList.append("Password must contain at least one lowercase letter.")

    if not re.search(r"[A-Z]", password): # rule 3: at least one uppercase letter (searches string input for uppercase letters)
        errorList.append("Password must contain at least one uppercase letter.")

    if not re.search(r"[0-9]", password): # rule 4: at least one digit (searches string input for digits)
        errorList.append("Password must contain at least one number.")

    if not re.search(r"[^A-Za-z0-9]", password): # rule 5: at least one symbol (not letter or number) (searches string input for symbols)
        errorList.append("Password must contain at least one symbol (e.g. !, @, #).")

    isValid = len(errorList) == 0 # if there are no error messages, the password is valid
    return isValid, errorList # returns the result and the list of errors if present
