import sys
import pdb
import numpy as np
from recipeFinder import getUrls
from recipeParser import parseRecipes
from classifier import generateMealPlan
from db import insertIngredientsAndRecipes


def generateCalibrationPksFromFile():
    filename = input("Enter calibration filename: ")
    #load file stuff
    print ("Reading calibration recipes from: " + str(filename))
    lines = [line.rstrip('\n') for line in open(filename)]
    calibrationUrls = []
    index = 0
    categories = ['breakfast', 'lunch', 'dinner']
    currUser = [[] for x in range(len(categories))]
    for line in lines:
        line = str(line)
        if line is '':
            calibrationUrls.append(currUser)
            break
        elif line in categories:
            index = categories.index(line)
        else:
            if currUser[index] is []:
                currUser[index] = line
            else:
                currUser[index].append(line)

    #inserting calibrated recipes into db
    for userRecipes in calibrationUrls:
        calibrationIngredients = []
        calibrationRecipes = []
        userPks = [[] for x in range(len(categories))]
        userInputNames = [[] for x in range(len(categories))]
        for i, category in enumerate(categories):
            categoryIngredients, categoryRecipes = parseRecipes(userRecipes[i], [category])
            insertIngredientsAndRecipes(categoryIngredients, categoryRecipes)
            categoryPks = []
            categoryInputNames = []
            for r in categoryRecipes:
                categoryPks.append(r.recipePk)
                categoryInputNames.append(r.name)

            userPks[i] = categoryPks
            userInputNames[i] = categoryInputNames
            calibrationRecipes.append(categoryRecipes)
            calibrationIngredients.append(categoryIngredients)

        print(userInputNames)
        print("INPUT: " + str(userInputNames) + "\n" + "OUTPUT: " + str(generateMealPlan(2, 7, userPks)))
        break

def scrapeAndPopulate():
    #page range for populating db in chunks
    start = 0
    stop = 150
    stop = 5
    pages = [(n, min(n+step, stop)) for n in xrange(start, stop, step)]
    pages.append((150, 1000))


    for pages in page_ranges:
        urls = getUrls(pages)
        for categoryUrls in urls:
            recipes = parseRecipes(categoryUrls[1], categoryUrls[0])
            insertIngredientsAndRecipes(recipes)

ans = input("Press 1 to scrape, 2 to test algorithm with input file: ")
if ans is '1':
    scrapeAndPopulate()
elif ans is '2':
    generateCalibrationPksFromFile()
