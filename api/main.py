# Import the Flask Framework
from flask import Flask, jsonify, abort, make_response, request, g
from flask_restful import Resource, Api, reqparse
from flask_httpauth import HTTPBasicAuth
from db import *
import sys

app = Flask(__name__)

# read from password file
try:
    lines = [line.rstrip('\n') for line in open('.secret_key')]
    secret_key = lines[0]
except Exception, exception:
    sys.exit("Couldn't get secret key. Does .secret_key exist?")

app.config['DEBUG'] = True
app.secret_key = secret_key
api = Api(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    entity = Entity.verify_auth_token(username_or_token)

    if not entity:
        # try to authenticate with username/password
        session = Session()
        entity = session.query(Entity).filter_by(username = username_or_token).first()

        if not entity or not entity.verify_password(password):
            return False

    g.entity = entity
    return True

# ensure that entities can only access their own resources (one entity can't modify another's mealplan)
# allow admins access to all resources
def validate_access(func):
    def decorator(*args, **kwargs):
        # chec entity has admin access
        session = Session()

	if not g.entity.is_admin:
            # if the entity isn't admin, give it access to resources it owns
            if 'entity_pk' not in kwargs or g.entity.entity_pk != kwargs['entity_pk']:
		res = make_response("Unauthorized Access")
		if res.status_code == 200:
		    # if user didn't set status code, use 401
		    res.status_code = 401
		if 'WWW-Authenticate' not in res.headers.keys():
		    res.headers['WWW-Authenticate'] = auth.authenticate_header()
		return res
        return func(*args, **kwargs)
    return decorator


###################################################
#############    Version 2      ###################
###################################################
class RecipesList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sort_by', required=False, type=str)
        super(RecipesList, self).__init__()

    @auth.login_required
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
        self.reqparse.add_argument('entity_pk', required=True, type=int, location='json')
        super(RecipeRatings, self).__init__()

    @auth.login_required
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

    @auth.login_required
    @validate_access
    def get(self):
        session = Session()
        entities = session.query(Entity).all()

        return map( lambda e: e.as_dict(), entities )

    def post(self):
        session = Session()
	new_entity = self.reqparse.parse_args()

        # check username
        existing_entity = session.query(Entity).filter(Entity.email == new_entity.email).first()
        if existing_entity is not None: # user exists
            return abort(400, "A user already exists with this email.")

        existing_entity = session.query(Entity).filter(Entity.username == new_entity.username).first()
        if existing_entity is not None: # user exists
            return abort(400, "A user already exists with this username.")

	entity = Entity(
	    first_name=new_entity.first_name,
	    last_name=new_entity.last_name,
	    username=new_entity.username,
	    email=new_entity.email
	)

	entity.hash_password(new_entity.password)

        session.add(entity)
        session.commit()

        g.entity = entity
        entity_dict = entity.as_dict()
        entity_dict['token'] = entity.generate_auth_token(60000)

        return entity_dict

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

    @auth.login_required
    @validate_access
    def get(self, entity_pk):
        session = Session()
        entity = session.query(Entity).filter_by(entity_pk=entity_pk).first()

        if(entity is None):
            abort(400, "This entity does not exist")

        return entity.as_dict()

    @auth.login_required
    def put(self, entity_pk):
        session = Session()
        # don't use g.entity incase the use is logged in as admin
        entity = session.query(Entity).filter_by(entity_pk=entity_pk).first()

        if(entity is None):
            abort(400, "This entity does not exist")

        params = self.reqparse.parse_args()

        if params['first_name'] is not None:
            entity.first_name = params['first_name']

        if params['last_name'] is not None:
            entity.last_name = params['last_name']

        if params['email'] is not None:
            existing_entity = session.query(Entity).filter_by(email=params['email']).first()
            if existing_entity is not None and existing_entity.entity_pk != g.entity.entity_pk:
                abort(400, "Someone already uses this email.")
            entity.email = params['email']

        if params['password'] is not None:
            if len(params['password']) < 6:
                abort(400, "Password must be at least 6 characters.")
            entity.password = params['password']

        if params['dietary_concerns'] is not None:
            dietary_concerns = params['dietary_concerns']

            for dietary_concern in dietary_concerns:
                tag = None
                if isinstance(dietary_concern, basestring):
                    dietary_concern = dietary_concern.lower().strip(' ')
                    tag = session.query(Tag).filter_by(name = dietary_concern, tag_type_pk = 1).first()
                elif isinstance(dietary_concern, int):
                    tag = session.query(Tag).filter_by(tag_pk = dietary_concern, tag_type_fk = 1).first()
                else:
                    abort(400, "Dietary concern tag must be an integer or a string.")

                if tag is None:
                    abort(400, "Dietary concern tag with primary key, " + str(tag) + ", does not exist.")

                if tag.tag_pk not in map(lambda t: t.tag_fk, entity.entity_tags): 
                    # if this entity doesn't have this dietary concern, add the dietary concern
                    entity_tag = EntityTag(entity_fk = entity.entity_pk, tag_fk = tag.tag_fk)
                    session.add(entity_tag)

        session.commit()

        return entity.as_dict()

    @auth.login_required
    @validate_access
    def delete(self, entity_pk):
        session = Session()
        entity = session.query(Entity).filter_by(entity_pk = entity_pk).first()
        if entity is None: # entity doesn't exist
            return None

        for entity_tag in entity.entity_tags:
            entity_tag = session.query(EntityTag).filter_by(entity_tag_pk = entity_tag.entity_tag_pk)
            session.delete(entity_tag)

        session.delete(entity)
        session.commit()

        return entity.as_dict()

class Tokens(Resource):
    @auth.login_required
    def get(self):
	token = g.entity.generate_auth_token(60000) # expires after 16.6 hours
	return { 'token': token.decode('ascii') }

    @auth.login_required
    def delete(self):
        #TODO store token in db and upon logout invalidate row
        pass

class EntityMealPlans(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('date', required = True, type=str)
        super(EntityMealPlans, self).__init__()

    @auth.login_required
    @validate_access
    def get(self, entity_pk):
        params = self.reqparse.parse_args()
        date = params['date']

        session = Session()

        if date is None:
            # default to current date
            day = time.day()
            month = time.month()
            year = time.year()
            date = day + '-' + month + '-' + year

        meal_plans = session.query(MealPlan).filter(MealPlan.entity_fk == entity_pk,  MealPlan.eat_on == date).all()

        if meal_plans is None:
            null

        meal_plan_dict = {}

        for meal_plan in meal_plans:
            if meal_plan.meal_type not in meal_plan_dict:
                meal_plan_dict[meal_plan.meal_type] = []
            meal_plan_dict[meal_plan.meal_type] = meal_plan.as_dict()

        return meal_plan_dict

api.add_resource(EntitiesList, '/api/v2.0/entities', endpoint = 'entitieslist')
api.add_resource(Entities, '/api/v2.0/entities/<int:entity_pk>', endpoint = 'entities')
api.add_resource(EntityMealPlans, '/api/v2.0/entities/<int:entity_pk>/meal_plans', endpoint = 'entitymealplans')
api.add_resource(RecipesList, '/api/v2.0/recipes', endpoint = 'recipes')
api.add_resource(RecipeRatings, '/api/v2.0/recipes/<int:recipe_pk>/rating', endpoint = 'recipesratings')
api.add_resource(Tokens, '/api/v2.0/tokens', endpoint = 'tokens')

@app.errorhandler(400)
def bad_request(e):
    return {'error': 'Bad Request'}, 400

@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

@app.errorhandler(500)
def internal_error(e):
    return make_response(jsonify({'error': 'An unexpected error occured'}), 500)

if __name__ == "__main__":
    app.run()
