import psycopg2
import datetime
import json
import os.path
from psycopg2.extras import NamedTupleConnection
from psycopg2.extras import RealDictCursor

def connect():
    try:
        conn=psycopg2.connect("dbname='intellichef' user='postgres' password='tB9gh2RS' host='35.185.59.20'")
        cur = conn.cursor()
    except Exception as e :
        print ("Unable to connect to the database.")
    return (conn, cur)

def disconnect(conn, cur):
    conn.close()
    cur.close()

# only takes a connection since db cursors should be created/destroyed
# with each query
def fetchall(conn, query, data=None):
    cur = execute(conn, query, (data,))
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
    except Exception as e:
        print(e)
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

def get_entity_pks():
    (conn, cur) = connect()
    query = """
    SELECT
        e.entity
    FROM tb_entity e
    """
    entity_pks = fetchall(conn, query)
    return entity_pks


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

def get_all_tag_recipes(conn, tag):
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
    JOIN tb_recipe_tag rt
    ON r.recipe = rt.recipe
    JOIN tb_tag t
    ON rt.tag = t.tag
    WHERE t.name = %s
    GROUP BY r.recipe, r.name, r.instructions, r.description, r.preparation_time
    """

    recipes = fetchall(conn, query, tag)
    return recipes

def get_calibration_recipe_pks(entity):
    categories = ['breakfast', 'lunch', 'dinner']
    (conn, cur) = connect()
    calibration_pks = []
    for tag in categories:
        calibration_pks.append(get_tag_calibration_recipe_pks(cur, entity, tag))
    conn.commit()
    disconnect(conn, cur)

    return calibration_pks

def get_tag_calibration_recipe_pks(cur, entity, tag):
    query = """
    SELECT rr.recipe FROM tb_entity_recipe_rating rr
    JOIN tb_recipe_tag rt
    ON rr.recipe = rt.recipe
    JOIN tb_tag t ON rt.tag = t.tag
    WHERE entity = %s
    AND is_calibration_recipe = 't'
    AND name = %s
    GROUP BY rr.recipe
    """
    data = (entity, tag)
    cur.execute(query, data)
    res = cur.fetchall()
    res = [int(x[0]) for x in res]
    return res


def insert_ingredients_and_recipes(recipes):
    (conn, cur) = connect()
    insert_recipeIngredients(recipes, cur)
    insert_recipeTags(recipes, cur)
    conn.commit()
    disconnect(conn, cur)

def insert_ingredients(ingredients, cur):
    for ingredient in ingredients:
        insert_ingredient(ingredient, cur)

def insert_ingredient(ingredient, cur):
    query = "INSERT INTO tb_ingredient (name) VALUES (%s) ON CONFLICT ON CONSTRAINT tb_ingredient_name_key DO UPDATE SET name = EXCLUDED.name returning ingredient;"
    cur.execute(query, [ingredient.name])
    ingredient.ingredientPk = cur.fetchone()[0]

def insert_recipe(r, cur):
    query = """INSERT INTO tb_recipe (name, description,preparation_time,instructions, image_url, serving_count, calories, fat, protein, carbs, cholesterol, sodium) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT tb_recipe_instructions_key DO UPDATE SET instructions = EXCLUDED.instructions returning recipe;"""
    data = (r.name, r.description, r.preparationTime, r.instructions, r.imageUrl, r.nutrition_info['servings'], r.nutrition_info['calories'], r.nutrition_info['fat'], r.nutrition_info['protein'], r.nutrition_info['carbs'], r.nutrition_info['cholesterol'], r.nutrition_info['sodium']);
    cur.execute(query, data)
    r.recipePk = cur.fetchone()[0];

def insert_recipeIngredients(recipes, cur):
    for r in recipes:
        insert_recipe(r, cur)
        for i in r.ingredients:
            insert_ingredient(i, cur)
            insert_recipeIngredient(r, i, cur)

def insert_recipeIngredient(r, i, cur):
    query = """INSERT INTO tb_ingredient_recipe (ingredient, recipe, quantity, unit, description) VALUES (%s, %s, %s, %s, %s);"""
    data = (i.ingredientPk, r.recipePk, i.quantity, i.unit, i.description);
    cur.execute(query, data)

def insert_recipeTags(recipes, cur):
    for r in recipes:
        if r.tags is not None:
            for t in r.tags:
                insert_recipeTag(r, t, cur)

def insert_recipeTag(r, t, cur):
    query = "INSERT INTO tb_recipe_tag (recipe, tag) VALUES (%s, (SELECT tag FROM tb_tag WHERE name = %s)) ON CONFLICT DO NOTHING;"""
    data = (r.recipePk, t)
    cur.execute(query, data)

def insert_meal_plan(entity, recipes, day):
    (conn, cur) = connect()
    categories = ['breakfast', 'lunch', 'dinner']
    start_day = day
    meal_plans = {}

    for i, category in enumerate(categories):
        meal_type = category
        day = start_day

        for r in recipes[i]:
            meal_plan = insert_meal(entity, r[0], str(day), meal_type, cur)
            if category not in meal_plans:
                meal_plans[category] = []
            meal_plans[category].append(meal_plan)

            day += datetime.timedelta(days=1)

    conn.commit()
    disconnect(conn, cur)
    return meal_plans

def insert_meal(entity, recipePk, day, meal_type, cur):
    query = """INSERT INTO tb_meal_plan (entity, recipe, eat_on, meal_type) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING entity, recipe, meal_plan;"""
    data = (entity, recipePk, day, meal_type);
    cur.execute(query, data)

    meal_plan = cur.fetchone()
    meal_plan_dict = {
        'entity_pk': meal_plan[0],
        'recipe_pk': meal_plan[1],
        'meal_plan_pk': meal_plan[2]
    }

    return json.loads((json.dumps(meal_plan_dict, indent=2)))

def get_ingredient_data():
    conn, cur = connect()

    ingredient_counts = get_total_ingredient_counts(conn)

    disconnect(conn, cur)

    return json.loads((json.dumps(ingredient_counts, indent=2)))

def get_recipe_data():
    conn, cur = connect()
    recipes = get_all_recipes(conn)
    disconnect(conn, cur)
    return json.loads((json.dumps(recipes, indent=2)))

def get_recipe_tag_data(tag):
    conn, cur = connect()
    recipes = get_all_tag_recipes(conn, tag)
    disconnect(conn, cur)
    return json.loads((json.dumps(recipes, indent=2)))

def get_user_likes(entityPk, tag):
    (conn, cur) = connect()
    query = """
    SELECT
        r.recipe,
        r.name
    FROM tb_recipe r
    JOIN tb_entity_recipe_rating rr
    ON r.recipe = rr.recipe
    JOIN tb_ingredient_recipe ir
    ON ir.recipe = r.recipe
    JOIN tb_ingredient i
    ON i.ingredient = ir.ingredient
    JOIN tb_recipe_tag rt
    ON r.recipe = rt.recipe
    JOIN tb_tag t
    ON rt.tag = t.tag
    WHERE rr.entity = %s AND t.name = %s AND rr.rating = 1
    GROUP BY r.recipe, r.name
    """
    cur = execute(conn, query, (entityPk, tag))
    recipes = cur.fetchall()
    cur.close()
    return recipes

def get_user_dislikes(entityPk, tag):
    (conn, cur) = connect()
    query = """
    SELECT
        r.recipe,
        r.name
    FROM tb_recipe r
    JOIN tb_entity_recipe_rating rr
    ON r.recipe = rr.recipe
    JOIN tb_ingredient_recipe ir
    ON ir.recipe = r.recipe
    JOIN tb_ingredient i
    ON i.ingredient = ir.ingredient
    JOIN tb_recipe_tag rt
    ON r.recipe = rt.recipe
    JOIN tb_tag t
    ON rt.tag = t.tag
    WHERE rr.entity = %s AND t.name = %s AND rr.rating = 0
    GROUP BY r.recipe, r.name
    """
    cur = execute(conn, query, (entityPk, tag))
    recipes = cur.fetchall()
    cur.close()
    return recipes
