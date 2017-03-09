import json
from webscraper.db import connect, disconnect, get_total_ingredient_counts, get_all_recipes, get_all_tag_recipes

def getIngredientData():
    conn, cur = connect()

    ingredient_counts = get_total_ingredient_counts(conn)

    disconnect(conn, cur)

    return json.loads((json.dumps(ingredient_counts, indent=2)))

def getRecipeData():
    conn, cur = connect()
    recipes = get_all_recipes(conn)
    disconnect(conn, cur)
    return json.loads((json.dumps(recipes, indent=2)))

def getRecipeTagData(tag):
    conn, cur = connect()
    recipes = get_all_tag_recipes(conn, tag)
    disconnect(conn, cur)
    return json.loads((json.dumps(recipes, indent=2)))

