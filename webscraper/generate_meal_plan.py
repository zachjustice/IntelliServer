#script to generate a meal plan for a given user using calibration recipes in the DB
#this script will also insert items into the db

from classifier import generateMealPlan

print(generateMealPlan(2, 7))

