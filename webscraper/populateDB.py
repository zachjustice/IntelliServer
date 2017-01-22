from recipeFinder import getUrls
from recipeParser import parseRecipes
from db import insertIngredientsAndRecipes

urls = getUrls()
ingredients, recipes = parseRecipes(urls)
ing = [x.name for x in ingredients]
#print(ing)
insertIngredientsAndRecipes(ingredients, recipes)
