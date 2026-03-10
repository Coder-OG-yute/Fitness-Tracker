# binary search function for a sorted list of names (used for exercise lookup in the exercise log page)


def binSearch(sortedNameList, targetName): # function to find the index of targetName using binary search
    """
    finds the index of targetName in sortedNameList using binary search
    sortedNameList must be sorted (A to Z)
    returns the index if found, or -1 if not in the list
    """
    lowIndex = 0 # lower bound of the search range
    highIndex = len(sortedNameList) - 1 # upper bound of the search range

    while lowIndex <= highIndex: # keep running as long as there is a range to search
        midIndex = (lowIndex + highIndex) // 2 # middle of the current range
        midValue = sortedNameList[midIndex].lower()
        targetLower = targetName.lower()

        if midValue == targetLower:
            return midIndex # item found, return its index
        elif targetLower < midValue:
            highIndex = midIndex - 1 # item is in the left half, move highIndex
        else:
            lowIndex = midIndex + 1 # item is in the right half, move lowIndex

    return -1 # item not found, return -1

