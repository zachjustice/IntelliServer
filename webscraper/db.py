import psycopg2
from psycopg2.extras import NamedTupleConnection
from psycopg2.extras import RealDictCursor

def connect():
    try:
        conn=psycopg2.connect("dbname='intellichef' user='jatin1' password='super123'")
        cur = conn.cursor()
    except:
        print ("Unable to connect to the database.")
    return (conn, cur)

def disconnect(conn, cur):
    conn.close()
    cur.close()

# only takes a connection since db cursors should be created/destroyed
# with each query
def fetchall(conn, query, data=None):
    cur = execute(conn, query, data)
    results = cur.fetchall()
    cur.close()
    return results

def execute(conn, query, data=None):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if data == None:
            cur.execute(query)
        else:
            cur.execute(query, data)
    except Exception:
        print("ERROR WITH QUERY: '" + query + "'")
    return cur

def get_total_ingredient_counts(conn):
    query = """
    SELECT ir.ingredient, i.name, count(ir.recipe)
    FROM tb_ingredient_recipe ir
    JOIN tb_ingredient i
    ON i.ingredient = ir.ingredient
    GROUP BY i.ingredient, ir.ingredient, i.name
    """

    ingredient_counts = fetchall(conn, query)
    return ingredient_counts

def get_all_recipes(conn):
    query = """
    SELECT
        r.recipe,
        r.name,
        r.instructions,
        r.description,
        array_agg(i.ingredient) as "ingredients",
        array_agg(i.name) as "ingredient_names"
    FROM tb_recipe r
    JOIN tb_ingredient_recipe ir
    ON ir.recipe = r.recipe
    JOIN tb_ingredient i
    ON i.ingredient = ir.ingredient
    GROUP BY r.recipe, r.name, r.instructions, r.description, r.preparation_time
    """

    recipes = fetchall(conn, query)
    return recipes

def insertIngredientsAndRecipes(ingredients, recipes):
    (conn, cur) = connect()
    insertIngredients(ingredients, cur)
    insertRecipes(recipes, cur)
    insertRecipeIngredients(recipes, cur)
    insertRecipeTags(recipes, cur)
    conn.commit()
    disconnect(conn, cur)

def insertIngredients(ingredients, cur):
    for ingredient in ingredients:
        insertIngredient(ingredient, cur)

def insertIngredient(ingredient, cur):
    query = "INSERT INTO tb_ingredient (name) VALUES (%s) ON CONFLICT ON CONSTRAINT tb_ingredient_name_key DO UPDATE SET name = EXCLUDED.name returning ingredient;"
    cur.execute(query, [ingredient.name])
    ingredient.ingredientPk = cur.fetchone()[0]

def insertRecipes(recipes, cur):
    for r in recipes:
        insertRecipe(r, cur)

def insertRecipe(r, cur):
    query = """INSERT INTO tb_recipe (name, description,preparation_time,instructions) VALUES (%s, %s, %s, %s) ON CONFLICT ON CONSTRAINT tb_recipe_instructions_key DO UPDATE SET instructions = EXCLUDED.instructions returning recipe;"""
    data = (r.name, r.description, r.preparationTime, r.instructions);
    cur.execute(query, data)
    r.recipePk = cur.fetchone()[0];

def insertRecipeIngredients(recipes, cur):
    for r in recipes:
        for i in r.ingredients:
            insertRecipeIngredient(r, i, cur)

def insertRecipeIngredient(r, i, cur):
    query = """INSERT INTO tb_ingredient_recipe (ingredient, recipe, quantity, unit, description) VALUES (%s, %s, %s, %s, %s);"""
    data = (i.ingredientPk, r.recipePk, i.quantity, i.unit, i.description);
    cur.execute(query, data)

def insertRecipeTags(recipes, cur):
    for r in recipes:
        if r.tags is not None:
            for t in r.tags:
                insertRecipeTag(r, t, cur)

def insertRecipeTag(r, t, cur):
    query = "INSERT INTO tb_recipe_tag (recipe, tag) VALUES (%s, (SELECT tag FROM tb_tag WHERE name = %s)) ON CONFLICT ON CONSTRAINT tb_recipe_tag_pkey DO NOTHING;"""
    data = (r.recipePk, t)
    cur.execute(query, data)
