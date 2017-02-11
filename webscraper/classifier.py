import json
import operator
import math
import numpy as np
from dump_recipe_and_ingredient_data import getIngredientData
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dump_recipe_and_ingredient_data import getRecipeData
from collections import defaultdict
from textblob import TextBlob as tb
from scipy import sparse

#highest level method - given a list of recipePks as 'userRecipes', generates a meal plan of 'mealPlanSize' recipes, considering 'calibrationThreshold' recipes from each calibration recipe
def generateMealPlan(userRecipes, mealPlanSize, calibrationThreshold):
    recipes = getRecipeData()
    tfidfMatrix = setupTfidfMatrix(recipes)
    matchingList = []
    for calibrationPk in userRecipes:
        matchingList.append(findSimilarRecipes(recipes, calibrationPk, calibrationThreshold, tfidfMatrix))
    return mergeLists(matchingList, userRecipes, mealPlanSize)

#merges recommendations from each base calibration recipe, uses a combination of two approaches
#1. If different calibration recipes produce the same match, it is more likely to appear in the output recommendation
#2. If each calibration recipe produces a distinct result, the most certain matches will appear in the output recommendation
def mergeLists(matchingLists, userRecipes, mealPlanSize):
    matchCount = defaultdict(int)
    aggregateMatches = []
    for match in matchingLists:
        for recipe in match:
            recipePk = round(float(recipe[1]))
            recipeName = recipe[2]
            key = (recipePk, recipeName)
            if recipePk not in userRecipes:
                matchCount[key] += 1
                aggregateMatches.append(recipe)

    recommendations = []
    sortedFreqMatches = np.array(sorted(matchCount.items(), key=operator.itemgetter(1)))[::-1]
    for match in sortedFreqMatches:
        if match[1] > 1 and len(recommendations) < mealPlanSize:
            recommendations.append(match[0])
        else:
            break

    sortedConfMatches = aggregateMatches[aggregateMatches[:][0].argsort()]
    print (sortedConfMatches)

    return recommendations

#given a single recipePk, generates 'calibrationThreshold' more recipes given a tfidfMatrix
def findSimilarRecipes(recipes, calibrationPk, calibrationThreshold, tfidfMatrix):
    recipeNames = np.array([r['name'] for r in recipes]).reshape((len(recipes), 1))
    recipePks = np.array([r['recipe'] for r in recipes])
    queryIndex = recipePks.tolist().index(calibrationPk)
    recipePks = recipePks.reshape((len(recipes), 1))

    results = cosine_similarity(tfidfMatrix[queryIndex][:], tfidfMatrix)
    results = np.vstack((results, recipePks.T))
    results = np.vstack((results, recipeNames.T))
    results = np.array(results).T

    sortedResults = results[results[:,0].argsort()[::-1]][1::]
    return (sortedResults[0:calibrationThreshold])


#computes a tfidf matrix based on recipe vocabulary
def setupTfidfMatrix(recipes):
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

print (generateMealPlan([620, 599, 619], 5, 5))

###################################################
#stuff to do tfidf manually - doesn't work as well as the library function, but might want to come back to it
def createDict():
    ingredients = getIngredientData()
    ingredientNames = [ingred['name'] for ingred in ingredients]
    ingredDictionary = defaultdict(int)
    for name in ingredientNames:
        for word in name.split():
            ingredDictionary[word] += 1
    return ingredDictionary


def vectorizeManual(ingredients, dic, numRecipes):
    wordList = ''
    for ingred in ingredients:
        wordList += ' '
        for w in ingred:
            wordList += w
    wordList = tb(wordList)
    tfidfDic = {}
    for word in wordList.words:
        tfScore = tf(word, wordList)
        idfScore = idf(word, dic, numRecipes)
        tfidfScore = tfScore * idfScore
        tfidfDic[word] = tfidfScore
    sorted_words = sorted(tfidfDic.items(), key=operator.itemgetter(1))

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def idf(word, dic, numRecipes):
    return math.log(numRecipes / (1 + dic[word]))
