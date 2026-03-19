# FatSecret API helper: gets calories and protein for a food name and mass FatSecret's API service used in my nutrition logging
# uses calling from web service API and parses JSON/XML to create a complex client-server model

from fatsecret import Fatsecret

#this is the API key for the FatSecret API
fs = Fatsecret("f352a037722240cf8abe2b7ebcdbe9c1", "d8b4d394d2764fcea6e42ee92060544d")


def getFoodMacro(foodInp, mass): # function to get calories and protein for a food from the FatSecret API
    """
    uses the FatSecret API to get calories and protein for a food

    1. search for the food name using foods_search (function from the FatSecret library)
    2. for simplicity i take the first result of the search and get its food_id from fatsecret
    3. calls the food_get(food_id) function to get detailed information from the FatSecret library
    4. Fatsecret doesn provide per 100g value so i calculate it myself by
       getting the first serving from the servings list and calculating the per 100g value
    5. scales calories and protein to the chosen mass in grams. returns dict with foodName, calories, protein or None
    """
    search = fs.foods_search(foodInp) # step 1: search for foods that match the input text

    if not search:
        return None # if the search list is empty, return None so the caller can handle it

    firstItem = search[0] # step 2: get the first result (index 0)
    foodName = firstItem.get("food_name") or firstItem.get("foodName")

    foodID = int(firstItem.get("food_id")) # step 3: get the food id from the first result
    detailFood = fs.food_get(foodID) # get the full details for this food using its ID

    servings = detailFood.get("servings") if detailFood else None # step 4: get the list of servings and take the first one
    if servings is None:
        return None
    servingList = servings.get("serving")

    if servingList is None: # FatSecret can return a dict or a list; we normalise to get one serving
        return None
    
    if isinstance(servingList, dict): # if the servingList is a dictionary, get the serving from the dictionary
        serving = servingList
    else:
        if len(servingList) == 0: # if the servingList is an empty list, return None 
            return None
        serving = servingList[0] # serving becomes the first item in the list if it is a list

    caloriesStr = serving.get("calories") # get raw value of calories from serving)
    proteinStr = serving.get("protein") # get raw value of protein from the serving
    servingMassStr = serving.get("metric_serving_amount") # get raw value of serving mass from the serving

    try: # convert string values to float so we can do calculations
        caloriesPerServing = float(caloriesStr)
        proteinPerServing = float(proteinStr)
        servingMass = float(servingMassStr)
    except (ValueError, TypeError): # if the values are not valid floats, return None
        return None

    if servingMass == 0: # step 5: work out amount per gram, then multiply by mass eaten for total amount
        return None # if serving mass is 0, return None so the variables can handle it
    
    perGram = 1 / servingMass
    totalCalories = round(caloriesPerServing * perGram * mass, 1)
    totalProtein = round(proteinPerServing * perGram * mass, 1)

    return {
        "foodName": foodName,
        "calories": totalCalories,
        "protein": totalProtein,
    } # returns the result dict for the caller