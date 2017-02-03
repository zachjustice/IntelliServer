entities = [
    {
        'entity'     : 1,
        'username'   : 'admin',
        'email'      : 'admin@intellichef.com',
        'password'   : '5CC',
        'first_name' : 'Intelli',
        'last_name'  : 'Chef',
        'logged_in'  : 'True'
    }
]

meal_plans = {
    '3-1-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    },
    '3-2-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    },
    '3-3-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    },
    '3-4-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    },
    '3-5-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    },
    '3-6-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    },
    '3-7-2017': {
        'breakfast':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'lunch':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        },
        'dinner':{
            'recipe':1,
            'name': 'Linguine',
            'instructions': 'Example Instructions',
            'description': 'Example Description'
        }
    }
}

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

    return entity


