# input validation utilities: validate numbers, dates, exercise input before saving to the database (used in the exercise log page)

def valNumb(value, min_value=None, max_value=None, allow_zero=True): # function to validate a number within custom range passed as parameter
    """
    validates that a value is a valid number within the specified range. returns (is_valid, error_message or None)
    """
    if value is None or value == "": # if value is empty, return False and error message
        return False, "Value cannot be empty"

    try: # try to convert value to a float
        numValue = float(value)
    except (ValueError, TypeError): # if conversion fails, return False and error message
        return False, "Value must be a number"

    if not allow_zero and numValue == 0: # if value is zero and allow_zero is False, return False and error message
        return False, "Value cannot be zero"

    if min_value is not None and numValue < min_value: # if value is less than min_value, return False and error message
        return False, f"Value must be at least {min_value}"

    if max_value is not None and numValue > max_value: # if value is greater than max_value, return False and error message
        return False, f"Value must be at most {max_value}"

    return True, None # if value is valid, return True and None


