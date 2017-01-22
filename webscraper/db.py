import psycopg2

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
    query = "INSERT INTO tb_ingredient (name) VALUES (%s) returning ingredient"
    cur.execute(query, [ingredient.name])
    ingredient.ingredientPk = cur.fetchone()[0]

def insertRecipes(recipes, cur):
    for r in recipes:
        insertRecipe(r, cur)

def insertRecipe(r, cur):
    query = """INSERT INTO tb_recipe (name, description,preparation_time,instructions) VALUES (%s, %s, %s, %s) returning recipe;"""
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
    query = "INSERT INTO tb_recipe_tag (recipe, tag) VALUES (%s, (SELECT tag FROM tb_tag WHERE name = %s))"
    data = (r.recipePk, t)
    cur.execute(query, data)
