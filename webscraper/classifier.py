import sys
import os
sys.path.append(os.path.abspath('./webscraper/'))
sys.path.append('/var/www/webscraper/')
import json
import operator
import math
import random
import numpy as np
from db import *
from datetime import datetime, timedelta
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from scipy import sparse

#highest level method for generating a mealplan - generates a mealplan for numDays days including breakfast, lunch, and dinner
#note: the userRecipes are expected to be a list of 3 lists - one for each mealType in the order [breakfast list], [lunch list], [dinner list]
def generate_meal_plan(entityPk, numDays, userRecipes = None, timeDelta = 0):
    #not testing, so grab input from DB
    if userRecipes is None:
        userRecipes = get_calibration_recipe_pks(entityPk)

    mealPlan = []
    duplicates = []
    #breakfast
    breakfastPks = userRecipes[0]
    mealPlan.append(generate_typed_meal_plan(breakfastPks, 'breakfast', numDays, duplicates))

    #lunch
    lunchPks = userRecipes[1]
    mealPlan.append(generate_typed_meal_plan(lunchPks, 'lunch', numDays, duplicates))

    #dinner
    dinnerPks = userRecipes[2]
    mealPlan.append(generate_typed_meal_plan(dinnerPks, 'dinner', numDays, duplicates))

    #insert into db
    today = datetime.now()
    today -= timedelta(timeDelta) #testing parameter, defaults no affect
    insert_meal_plan(entityPk, mealPlan, today)
    return mealPlan

#given a list of recipePks as 'userRecipes', generates a meal plan of 'mealPlanSize' recipes, considering 'calibrationThreshold' recipes from each calibration recipe
def generate_typed_meal_plan(userRecipes, mealType, mealPlanSize = 7, duplicates = [], calibrationThreshold = 7):
    recipes = get_recipe_tag_data(mealType)
    store = [r['recipe'] for r in recipes]
    if len(userRecipes) == 0:
        userRecipes.append(random.choice(recipes)['recipe'])
    tfidfMatrix = setup_tfidf_matrix(recipes)
    matchingList = []
    for calibrationPk in userRecipes:
        matchingList.append(find_similar_recipes(recipes, int(calibrationPk), calibrationThreshold, tfidfMatrix))
    return merge_lists(matchingList, userRecipes, mealPlanSize, duplicates)

#merges recommendations from each base calibration recipe, uses a combination of two approaches
#1. If different calibration recipes produce the same match, it is more likely to appear in the output recommendation
#2. If each calibration recipe produces a distinct result, the most certain matches will appear in the output recommendation
def merge_lists(matchingLists, userRecipes, mealPlanSize, duplicates):
    matchCount = defaultdict(int)
    aggregateMatches = []
    for match in matchingLists:
        for recipe in match:
            recipeName = recipe[1]
            recipePk = int(recipe[2])
            key = (recipePk, recipeName)
            if key not in duplicates:
                if recipePk not in userRecipes:
                    matchCount[key] += 1
                    aggregateMatches.append(recipe)

    recommendations = []
    sortedFreqMatches = np.array(sorted(matchCount.items(), key=operator.itemgetter(1)))[::-1]
    aggregateMatches = np.array(aggregateMatches)
    sortedConfMatches = aggregateMatches[aggregateMatches[:,0].argsort()][::-1]
    sortedConfMatches = [(int(match[2]), match[1]) for match in sortedConfMatches]

    freqIndex = 0
    confIndex = 0
    while len(recommendations) < mealPlanSize:
        freqMatch = sortedFreqMatches[freqIndex]
        confMatch = sortedConfMatches[confIndex]
        if freqMatch[1] > 1:
            recommendations.append(freqMatch[0])
            duplicates.append(freqMatch[0])
            freqIndex += 1
        elif confMatch not in recommendations:
            recommendations.append(confMatch)
            duplicates.append(confMatch)
            confIndex += 1
        else:
            confIndex += 1

    return recommendations

#given a single recipePk, generates 'calibrationThreshold' more recipes given a tfidfMatrix
def find_similar_recipes(recipes, calibrationPk, calibrationThreshold, tfidfMatrix):
    recipeNames = np.array([r['name'] for r in recipes]).reshape((len(recipes), 1))
    recipePks = np.array([int(float(r['recipe'])) for r in recipes])
    queryIndex = recipePks.tolist().index(calibrationPk)
    recipePks = recipePks.reshape((len(recipes), 1))

    results = cosine_similarity(tfidfMatrix[queryIndex][:], tfidfMatrix)
    results = np.vstack((results, recipeNames.T))
    results = np.vstack((results, recipePks.T))
    results = np.array(results).T

    sortedResults = results[results[:,0].argsort()[::-1]][1::]
    return (sortedResults[0:calibrationThreshold])


#computes a tfidf matrix based on recipe vocabulary
def setup_tfidf_matrix(recipes):
    documents = []
    for r in recipes:
        documents.append(vectorize(r['ingredient_names']))

    tfidfVectorizer = TfidfVectorizer()
    tfidfMatrix = tfidfVectorizer.fit_transform(documents)
    tfidfMatrix = tfidfMatrix.tocsr()
    return tfidfMatrix

#translates ingredient list into a vocabulary
def vectorize(ingredients):
    wordList = ''
    for ingred in ingredients:
        wordList += ' '
        for w in ingred:
            wordList += w
    return wordList


###################################################
#stuff to do tfidf manually - doesn't work as well as the library function, but might want to come back to it
#def createDict():
#    ingredients = get_ingredient_data()
#    ingredientNames = [ingred['name'] for ingred in ingredients]
#    ingredDictionary = defaultdict(int)
#    for name in ingredientNames:
#        for word in name.split():
#            ingredDictionary[word] += 1
#    return ingredDictionary
#
#
#def vectorizeManual(ingredients, dic, numRecipes):
#    wordList = ''
#    for ingred in ingredients:
#        wordList += ' '
#        for w in ingred:
#            wordList += w
#    wordList = tb(wordList)
#    tfidfDic = {}
#    for word in wordList.words:
#        tfScore = tf(word, wordList)
#        idfScore = idf(word, dic, numRecipes)
#        tfidfScore = tfScore * idfScore
#        tfidfDic[word] = tfidfScore
#    sorted_words = sorted(tfidfDic.items(), key=operator.itemgetter(1))
#
#def tf(word, blob):
#    return blob.words.count(word) / len(blob.words)
#
#def idf(word, dic, numRecipes):
#    return math.log(numRecipes / (1 + dic[word]))
