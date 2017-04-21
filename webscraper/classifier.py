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
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from numpy.random import choice
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
    mealPlan.append(generate_typed_meal_plan(entityPk, breakfastPks, 'breakfast', numDays, duplicates))

    #lunch
    lunchPks = userRecipes[1]
    mealPlan.append(generate_typed_meal_plan(entityPk, lunchPks, 'lunch', numDays, duplicates))

    #dinner
    dinnerPks = userRecipes[2]
    mealPlan.append(generate_typed_meal_plan(entityPk, dinnerPks, 'dinner', numDays, duplicates))

    #insert into db
    today = datetime.now()
    today -= timedelta(timeDelta) #testing parameter, defaults no affect
    created_meal_plans = insert_meal_plan(entityPk, mealPlan, today)

    return created_meal_plans

#given a list of recipePks as 'userRecipes', generates a meal plan of 'mealPlanSize' recipes, considering 'calibrationThreshold' recipes from each calibration recipe
def generate_typed_meal_plan(entityPk, userRecipes, mealType, mealPlanSize = 7, duplicates = [], calibrationThreshold = 20):
    recipes = get_recipe_tag_data(mealType)
    if len(userRecipes) == 0:
        userRecipes.append(random.choice(recipes)['recipe'])

    tfidfMatrix = setup_tfidf_matrix(recipes, mealType, needs_update = False)
    matchingList = []
    for calibrationPk in userRecipes:
        matchingList.append(find_similar_recipes(recipes, int(calibrationPk), calibrationThreshold, tfidfMatrix))

    likedList = []
    likedRecipes = get_user_likes(entityPk, mealType)
    for like in likedRecipes:
        likedList.append(find_similar_recipes(recipes, int(like['recipe']), calibrationThreshold, tfidfMatrix))


    dislikedList = []
    dislikedRecipes = get_user_dislikes(entityPk, mealType)
    for dislike in dislikedRecipes:
        sim_dislikes = find_similar_recipes(recipes, int(dislike['recipe']), calibrationThreshold, tfidfMatrix)
        this_recipe = np.array(['1.0', dislike['name'], str(dislike['recipe'])])
        sim_dislikes = np.concatenate((sim_dislikes, [this_recipe]))
        dislikedList.append(sim_dislikes)

    return merge_lists(matchingList, userRecipes, mealPlanSize, duplicates, likedList, dislikedList)

#merges recommendations from each base calibration recipe, uses a combination of two approaches
#1. If different calibration recipes produce the same match, it is more likely to appear in the output recommendation
#2. If each calibration recipe produces a distinct result, the most certain matches are more likely to appear in the output recommendation
def merge_lists(matchingLists, userRecipes, mealPlanSize, duplicates, likedList, dislikedList):
    matchCount = defaultdict(int)
    aggregateMatches = []

    #populate blacklist based off of dislikes
    blacklist = []
    for dislike in dislikedList:
        for dislikedRecommendation in dislike:
            recipeName = dislikedRecommendation[1]
            recipePk = int(dislikedRecommendation[2])
            key = (recipePk, recipeName)
            blacklist.append(key)

    #populate recommendations based on calibration recipes
    for match in matchingLists:
        for recipe in match:
            recipeName = recipe[1]
            recipePk = int(recipe[2])
            key = (recipePk, recipeName)
            if key not in duplicates and key not in blacklist:
                matchCount[key] += 1
                aggregateMatches.append(recipe)

    #populate recommendations based on likes
    for like in likedList:
        for likedRecommendation in like:
            recipeName = likedRecommendation [1]
            recipePk = int(likedRecommendation[2])
            key = (recipePk, recipeName)
            if key not in duplicates and key not in blacklist:
                matchCount[key] += 1
                aggregateMatches.append(likedRecommendation)


    recommendations = []
    sortedFreqMatches = np.array(sorted(matchCount.items(), key=operator.itemgetter(1)))[::-1]
    aggregateMatches = np.array(aggregateMatches)
    confWeights = [float((match[0]))  for match in aggregateMatches]
    noise = np.random.normal(-0.1,0.1,len(confWeights))
    confWeights = [x + y for x, y in zip(confWeights, noise)]
    tot = sum([w for w in confWeights])
    normalizedConfWeights = [w / tot for w in confWeights]

    aggregateMatches = [(match[2], match[1]) for match in aggregateMatches]

    #frequency matches first
    for freqMatch in sortedFreqMatches:
        if freqMatch[1] > 1:
            recommendations.append(freqMatch[0])
            duplicates.append(freqMatch[0])
        else:
            break

    #sample from normalized confidence matches distribution
    #confIndices = choice(len(aggregateMatches), mealPlanSize, p=normalizedConfWeights, replace=False)
    confIndices = choice(len(aggregateMatches), mealPlanSize, replace=False)
    confMatches = [aggregateMatches[i] for i in confIndices]

    #make sure it wasn't a freq match
    for match in confMatches:
        if match not in recommendations:
            recommendations.append(match)

    return recommendations[0:mealPlanSize]

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
    return sortedResults[0:calibrationThreshold]


#computes a tfidf matrix based on recipe vocabulary
def setup_tfidf_matrix(recipes, mealType, needs_update):
    #recompute matrix because db changed
    if needs_update:
        documents = []
        for r in recipes:
            documents.append(vectorize(r['ingredient_names']))

        tfidfVectorizer = TfidfVectorizer()
        tfidfMatrix = tfidfVectorizer.fit_transform(documents)
        tfidfMatrix = tfidfMatrix.tocsr()
        np.savez('tfidf_' + str(mealType) + '.npz',data = tfidfMatrix.data ,indices=tfidfMatrix.indices,
                             indptr =tfidfMatrix.indptr, shape=tfidfMatrix.shape )
        return tfidfMatrix
    else:
        loader = np.load('tfidf_' + str(mealType) + '.npz')
        return csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                            shape = loader['shape'])


#translates ingredient list into a vocabulary
def vectorize(ingredients):
    wordList = ''
    for ingred in ingredients:
        wordList += ' '
        for w in ingred:
            wordList += w
    return wordList

