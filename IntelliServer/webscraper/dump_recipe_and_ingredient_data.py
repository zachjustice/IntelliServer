import json
from db import connect, disconnect, get_total_ingredient_counts, get_all_recipes

conn, cur = connect()

ingredient_counts = get_total_ingredient_counts(conn)
recipes = get_all_recipes(conn)

disconnect(conn, cur)

print (json.dumps(ingredient_counts, indent=2))
print (json.dumps(recipes, indent=2))

