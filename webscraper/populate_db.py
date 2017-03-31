import sys
import numpy as np
from recipe_finder import get_urls
from recipe_parser import parse_recipes
from classifier import generate_meal_plan
from db import insert_ingredients_and_recipes


def generate_calibration_pks_from_file():
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
            categoryIngredients, categoryRecipes = parse_recipes(userRecipes[i], [category])
            insert_ingredients_and_recipes(categoryIngredients, categoryRecipes)
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
        print("INPUT: " + str(userInputNames) + "\n" + "OUTPUT: " + str(generate_meal_plan(2, 7, userPks)))
        break

def scrape_and_populate():
    #page range for populating db in chunks
    start = 0
    stop = 150
    step = 5
    page_ranges = [(0, 1)]
    #page_ranges = [(n, min(n+step, stop)) for n in range(start, stop, step)]
    #uncomment for last section only (lunch/dinner meals)
    #page_ranges = []
    #page_ranges.append((150, 1000))
    for pages in page_ranges:
        urls = get_urls(pages)
        for categoryUrls in urls:
            recipes = parse_recipes(categoryUrls[1], categoryUrls[0])
            insert_ingredients_and_recipes(recipes)

#ans = input("Press 1 to scrape, 2 to test algorithm with input file: ")
#if ans is '1':
#    scrape_and_populate()
#elif ans is '2':
#    generate_calibration_pks_from_file()

scrape_and_populate()
