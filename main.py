# Import the Flask Framework
import api_v1
from flask import Flask, jsonify, abort, make_response, request
from flask_restful import Resource, Api, reqparse
from db import get_entity, update_entity, delete_entity, get_meal_plan

app = Flask(__name__)
api = Api(app)

###################################################
#############    Version 2      ###################
###################################################

class Entities(Resource):
    def get(self):
        return {'entities': entities}

class Entity(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email'     , required=True, type=str, location='json')
        self.reqparse.add_argument('password'  , required=False,type=str, location='json')
        self.reqparse.add_argument('first_name', required=True, type=str, location='json')
        self.reqparse.add_argument('last_name' , required=True, type=str, location='json')
        super(Entity, self).__init__()

    def get(self, entity_pk):
        entity = get_entity(entity_pk)
        if(entity is None or entity == False):
            abort(400)
        else:
            return entity

    def put(self, entity_pk):
        entity = get_entity(entity_pk)
        if(entity is None or entity == False):
            return abort(400)

	args = self.reqparse.parse_args()
	updated_entity = update_entity( entity_pk, args )
        return updated_entity

    def delete(self, entity_pk):
        return {'deleted_entity': delete_entity(entity_pk)}

class MealPlan(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('date' , required=True, type=str)
        super(MealPlan, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        date = args['date']
        meal_plan = get_meal_plan(date)

        if(meal_plan is None):
            abort(400)
        else:
            return meal_plan

api.add_resource(Entities, '/api/v2.0/entities',                  endpoint = 'entities')
api.add_resource(Entity,    '/api/v2.0/entities/<int:entity_pk>', endpoint = 'entity')
api.add_resource(MealPlan, '/api/v2.0/meal_plan',                 endpoint = 'mealplan')

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

    entities.append({
        'email' : email,
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
    return make_response(jsonify({'error': 'Bad Request: ' + e.description}), 400)

@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(405)
def application_error(e):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

@app.errorhandler(500)
def application_error(e):
    return make_response(jsonify({'error': 'An unexpected error occured'}), 500)
