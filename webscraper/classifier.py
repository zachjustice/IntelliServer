import json
import operator
import math
import numpy as np
from pprint import pprint
from dump_recipe_and_ingredient_data import getIngredientData
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dump_recipe_and_ingredient_data import getRecipeData
from collections import defaultdict
from textblob import TextBlob as tb

def vectorize(ingredients):
    wordList = ''
    for ingred in ingredients:
        wordList += ' '
        for w in ingred:
            wordList += w
    return wordList

def generateMealPlan(userRecipes, size):
    matchingList = []
    for r in userRecipes:
        matchingList.append(findSimilarRecipes(r))
    return mergeLists(matchingList, size)

def mergeLists(matchingLists, size):
    matchCount = {}
    for match in matchingLists:
        for recipe in match:
            matchCount[recipe] += 1

    recommendations = []
    sortedMatches = sorted(matchCount.items(), key=operator.itemgetter(1))
    i = 0
    while i < size:
        recommendations.append(sortedMatches[i])
    return recommendations

def findSimilarRecipes():
    recipes = getRecipeData()
    documents = []
    for r in recipes:
        documents.append(vectorize(r['ingredient_names']))
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    results = (np.sort((cosine_similarity(tfidf_matrix[0:1], tfidf_matrix))))
    sortedResults = np.fliplr(results)

findSimilarRecipes()

###################################################
#stuff to do tfidf manually - doesn't work as well as the library function, so it's just wasted time T_T
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
