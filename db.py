entities = [
    {
        'entity'     : 1,
        'username'   : 'admin',
        'email'      : 'admin@intellichef.com',
        'password'   : '5CC',
        'first_name' : 'Intelli',
        'last_name'  : 'Chef',
        'logged_in'  : 'True',
        'allergies'  : [],
        'dietary_concerns' : []
    },
    {
        'entity'     : 2,
        'username'   : 'user',
        'email'      : 'user@intellichef.com',
        'password'   : '5CC',
        'first_name' : 'Zach',
        'last_name'  : 'Bubble',
        'logged_in'  : 'True',
        'allergies'  : [],
        'dietary_concerns' : []
    }
]

recipes = [
    {
        'recipe':1,
        'name': 'Saucy Slow Cooker Pork Chops',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/1055211.jpg',
        'is_calibration_recipe': True,
        'rating': 4.5
    },
    {
        'recipe':2,
        'name': 'Roasted Vegetables',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/1486.jpg',
        'rating': 4.5
    },
    {
        'recipe':3,
        'name': 'Guacamole',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/811729.jpg',
        'is_calibration_recipe': True,
        'rating': 5
    },
    {
        'recipe':4,
        'name': 'Addictive Sesame Chicken',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/250x250/674239.jpg',
        'rating': 4.5
    },
    {
        'recipe':5,
        'name': 'Lentil Soup',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/789512.jpg',
        'rating': 4.5
    },
    {
        'recipe':6,
        'name': 'Banana Pancakes',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/708583.jpg',
        'rating': 4.5
    },
    {
        'recipe':7,
        'name': 'Oven Roasted Red Potatoes',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/722998.jpg',
        'rating': 4.5
    },
    {
        'recipe':8,
        'name': 'Copycat Panera Broccoli Cheddar Soup',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/1087142.jpg',
        'rating': 4.5
    },
    {
        'recipe':9,
        'name': 'Black Bean and Corn Quesadillas',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/829340.jpg',
        'rating': 4.5
    },
    {
        'recipe':10,
        'name': 'Asian Tuna with Poached Egg',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/3511815.jpg',
        'rating': 5
    },
    {
        'recipe':11,
        'name': 'World\'s Best Lasagna',
        'instructions': 'Example Instructions',
        'description': 'Example Description',
        'is_calibration_recipe': True,
        'url': 'http://images.media-allrecipes.com/userphotos/720x405/3359675.jpg',
        'rating': 5
    },
]

meal_plans = {
    '3-1-2017': {
        'breakfast': recipes[0],
        'lunch': recipes[1],
        'dinner': recipes[2]
    },
    '3-2-2017': {
        'breakfast': recipes[3],
        'lunch': recipes[4],
        'dinner': recipes[5]
    },
    '3-3-2017': {
        'breakfast': recipes[6],
        'lunch': recipes[7],
        'dinner': recipes[8]
    },
    '3-4-2017': {
        'breakfast': recipes[9],
        'lunch': recipes[10],
        'dinner': recipes[3]
    },
    '3-5-2017': {
        'breakfast': recipes[2],
        'lunch': recipes[4],
        'dinner': recipes[3]
    },
    '3-6-2017': {
        'breakfast': recipes[2],
        'lunch': recipes[8],
        'dinner': recipes[9]
    },
    '3-7-2017': {
        'breakfast': recipes[0],
        'lunch': recipes[3],
        'dinner': recipes[4]
    }
}

def get_recipes():
    return recipes

def get_calibration_recipes():
    return filter(lambda r: r['is_calibration_recipe'] == True, recipes)

def get_most_popular_recipes():
    return sorted(recipes, cmp=lambda y, x: int(round(x['rating'] - y['rating'])))

def create_or_update_recipe_rating( recipe_rating ):
    return recipe_rating

def create_entity(new_entity):
    last_entity = max(entities, key=lambda e: e['entity'])
    new_entity['entity'] = last_entity['entity'] + 1
    new_entity['logged_in'] = True
    entities.append(new_entity)

    return new_entity

def get_meal_plan(date):
    if( date not in meal_plans ):
        return None
    return meal_plans[date]

def get_entity( entity_identifier ):
    entity = filter(
        lambda e: e['email'] == entity_identifier or e['username'] == entity_identifier or e['entity'] == entity_identifier,
        entities
    )

    if len(entity) == 0:
        return False
    if len(entity) > 1:
        return None

    return entity[0]

def delete_entity(entity_pk):
    for i in xrange(len(entities)):
        if(entities[i]['entity'] == entity_pk):
            del entities[i]
            return True

    return False

def update_entity( entity_pk, updated_entity ):
    entity = filter(lambda e: e['entity'] == entity_pk, entities)

    if len(entity) != 1:
        return None

    entity = entity[0]
    if( 'email' in updated_entity and updated_entity['email'] is not None ):
        entity['email'] = updated_entity['email']

    if( 'password' in updated_entity and updated_entity['password'] is not None ):
        entity['password'] = updated_entity['password']

    if( 'first_name' in updated_entity and updated_entity['first_name'] is not None ):
        entity['first_name'] = updated_entity['first_name']

    if( 'last_name' in updated_entity and updated_entity['last_name'] is not None ):
        entity['last_name'] = updated_entity['last_name']

    if( 'allergies' in updated_entity and updated_entity['allergies'] is not None ):
        entity['allergies'] = updated_entity['allergies']

    if( 'dietary_concerns' in updated_entity and updated_entity['dietary_concerns'] is not None ):
        entity['dietary_concerns'] = updated_entity['dietary_concerns']

    return entity


