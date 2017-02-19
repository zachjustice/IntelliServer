import sys
from recipeFinder import getUrls
from recipeParser import parseRecipes
from classifier import generateMealPlan
from db import insertIngredientsAndRecipes

def generateCalibrationPksFromFile():
    if len(sys.argv) > 1:
        #load file stuff
        print ("Reading calibration recipes from: " + str(sys.argv[1]))
        filename = sys.argv[1]
        lines = [line.rstrip('\n') for line in open(filename)]
        calibrationUrls = []
        currUser = []
        for line in lines:
            if line is '':
                calibrationUrls.append(currUser)
                currUser = []
            else:
                currUser.append(line)

        #inserting calibrated recipes into db
        for userRecipes in calibrationUrls:
            userPks = []
            userInputNames = []
            calibrationIngredients, calibrationRecipes = parseRecipes(userRecipes)
            insertIngredientsAndRecipes(calibrationIngredients, calibrationRecipes)
            for r in calibrationRecipes:
                userPks.append(r.recipePk)
                userInputNames.append(r.name)
            print("INPUT: " + str(userInputNames) + "\n" + "OUTPUT: " + str(generateMealPlan(userPks)))
    else:
        print ("Enter the filename as a command line argument!")
        sys.exit(0)

def scrapeAndPopulate():
    urls = getUrls()
    ingredients, recipes = parseRecipes(urls)
    insertIngredientsAndRecipes(ingredients, recipes)


generateCalibrationPksFromFile()
#scrapeAndPopulate()
