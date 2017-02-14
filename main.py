# Import the Flask Framework
from flask import Flask, jsonify, abort, make_response, request
from flask_restful import Resource, Api, reqparse
from db import *

app = Flask(__name__)
app.config['DEBUG'] = True
api = Api(app)

###################################################
#############    Version 2      ###################
###################################################
class RecipesList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sort_by', required=False, type=str)
        super(RecipesList, self).__init__()

    def get(self):
	recipe_params = self.reqparse.parse_args()
        if recipe_params['sort_by'] == 'popular':
            return get_most_popular_recipes()
        if recipe_params['sort_by'] == 'calibration_recipes':
            return get_calibration_recipes()
        return get_recipes()

class RecipeRatings(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('recipe', required=True, type=int, location='json')
        self.reqparse.add_argument('rating', required=True, type=int, location='json')
        self.reqparse.add_argument('entity', required=True, type=int, location='json')
        super(RecipeRatings, self).__init__()

    def post(self):
	recipe_rating = self.reqparse.parse_args()
        recipe_rating = create_or_update_recipe_rating( recipe_rating )

        if( recipe_rating is None ):
            abort( 500 )

        return recipe_rating

class EntitiesList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email'     ,       required=True, type=str, location='json')
        self.reqparse.add_argument('password'  ,       required=True, type=str, location='json')
        self.reqparse.add_argument('first_name',       required=True, type=str, location='json')
        self.reqparse.add_argument('last_name' ,       required=True, type=str, location='json')
        self.reqparse.add_argument('username'  ,       required=True, type=str, location='json')
        super(EntitiesList, self).__init__()

    def get(self):
        return {'entities': entities}

    def post(self):
	new_entity = self.reqparse.parse_args()
        for entity_identifier in [new_entity['username'], new_entity['email']]:
            entity = get_entity(entity_identifier) # returns false is user doesn't exist
            if(entity is None ):
                return abort(500)
            if(entity != False): # user exists
                return abort(400, "A user already exists with this username or email.")

	new_entity = create_entity(new_entity)
        return new_entity

class Entities(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        self.reqparse.add_argument('first_name', type=str, location='json')
        self.reqparse.add_argument('last_name', type=str, location='json')
        self.reqparse.add_argument('allergies', type=list, location='json')
        self.reqparse.add_argument('dietary_concerns', type=list, location='json')
        super(Entities, self).__init__()

    def get(self, entity_pk):
        entity = get_entity(entity_pk)
        if(entity is None):
            abort(500)
        if(entity == False):
            abort(400, "This entity does not exist")
        else:
            return entity

    def put(self, entity_pk):
        entity = get_entity(entity_pk)
        if(entity is None):
            abort(500)
        if(entity == False):
            abort(400, "This entity does not exist")

	args = self.reqparse.parse_args()
	updated_entity = update_entity( entity_pk, args )
        return updated_entity

    def delete(self, entity_pk):
        if( delete_entity(entity_pk)):
            return {'deleted_entity': True}
        else:
            abort(400, 'This entity does not exist')

class MealPlans(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('date' , required=False, type=str)
        super(MealPlans, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        date = args['date']

        if date is None:
            # if no meal plan is specified return the last 10
            return meal_plans

        meal_plan = get_meal_plan(date)

        if(meal_plan is None):
            abort(400, "No meal plan exists for the date {}".format(date))
        return meal_plan

api.add_resource(EntitiesList, '/api/v2.0/entities', endpoint = 'entitieslist')
api.add_resource(Entities, '/api/v2.0/entities/<int:entity_pk>', endpoint = 'entities')
api.add_resource(MealPlans, '/api/v2.0/meal_plans', endpoint = 'mealplans')
api.add_resource(RecipesList, '/api/v2.0/recipes', endpoint = 'recipes')
api.add_resource(RecipeRatings, '/api/v2.0/recipes/<int:recipe_pk>/rating', endpoint = 'recipesratings')

###################################################
#############    Version 1      ###################
###################################################

@app.route( '/api/v1.0/login', methods=['POST'] )
def login():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400, 'Email and password must be provided.')

    entity = _get_entity_by_email_and_password( request.json['email'], request.json['password'] )
    if( entity is not None ):
        entity['logged_in'] = True
        return jsonify({'status': True})
    else:
        # user doesn't exist so logging in is false
        return jsonify({'status': False})

def _get_entity_by_email_and_password( email, password ):
    matching_entity = filter(
        lambda entity: entity['email'] == email and entity['password'] == password,
        entities
    )

    if len( matching_entity ) > 0:
        return matching_entity[0]

    return None

@app.route( '/api/v1.0/register', methods=['POST'] )
def register():
    if( not request.json
    or not 'email' in request.json
    or not 'username' in request.json
    or not 'password' in request.json
    or not 'firstName' in request.json
    or not 'lastName' in request.json
    or not 'password' in request.json ):
        abort(400, 'Registration information is missing.')

    email = request.json['email']
    username = request.json['username']

    matching_entities = filter(
        lambda entity: entity['username'] == username or entity['email'] == email,
        entities
    )

    if len( matching_entities ) > 0:
        # The user already exists so notify user registration is false
        return jsonify({'status': False})

    last_entity = max(entities, key=lambda e: e['entity'])

    entities.append({
        'email' : email,
        'entity' : last_entity['entity'] + 1,
        'username' : username,
        'password' : request.json['password'],
        'first_name' : request.json['firstName'],
        'last_name' : request.json['lastName'],
        'logged_in' : True
    })

    return jsonify({'status': True})

@app.route( '/api/v1.0/entities', methods=['GET']  )
def get_entities():
    return jsonify({'entities': entities})

@app.route( '/api/v1.0/logout', methods=['PUT'] )
def logout():
    if not request.json or not 'email' in request.json:
        abort(400, 'Email must be provided.')

    matching_entity = filter(
        lambda entity: entity['email'] == request.json['email'],
        entities
    )

    if len( matching_entity ) > 1:
        # Data integrity error so fail
        abort(400, 'More than email was found when logging out user.')
    if len( matching_entity ) == 0:
        # Using an email which doesn't exist so fail
        abort(400, 'This user account does not exist.')
    else:
        matching_entity = matching_entity[0]

    matching_entity['logged_in'] = False
    return jsonify({'status': True})

@app.route( '/api/v1.0/remove_account', methods=['POST'] )
def remove_account():
    if not request.json or not 'email' in request.json:
        abort(400, 'Email must be provided.')

    matching_entity = filter(
        lambda entity: entity['email'] == request.json['email'],
        entities
    )

    if len( matching_entity ) > 1:
        # data integrity error so fail
        abort(400, 'More than one email found when removing user account.')
    if len( matching_entity ) == 0:
        # don't need to remove anything, return false
        return jsonify({'status': False})
    else:
        del entities[entities.index(matching_entity[0])]

    return jsonify({'status': True})

@app.errorhandler(400)
def page_not_found(e):
    return {'error': 'Bad Request'}, 400

@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(405)
def application_error(e):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

@app.errorhandler(500)
def application_error(e):
    return make_response(jsonify({'error': 'An unexpected error occured'}), 500)
