from flask import Flask, jsonify, abort, make_response, request, g
from flask_restful import Resource, Api, reqparse
from flask_httpauth import HTTPBasicAuth
from webscraper import *
from api.models import *
from api import app, Session

my_api = Api(app) # resources are added to this object
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    entity = Entity.verify_auth_token(username_or_token)

    if entity is None:
        # try to authenticate with username/password
        session = Session()
        entity = session.query(Entity).filter_by(username = username_or_token).first()
        entities = session.query(Entity).all()

        if not entity or not entity.verify_password(password):
            return False

    g.entity = entity
    return True

# ensure that entities can only access their own resources (one entity can't modify another's mealplan)
# allow admins access to all resources
def validate_access(func):
    def decorator(*args, **kwargs):
        # chec entity has admin access
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

class Recipes(Resource):
    @auth.login_required
    def get(self, recipe_pk):
        session = Session()
        recipe = session.query(Recipe).filter_by(recipe=recipe_pk).first()
        if recipe is None:
            abort(400, "Recipe not found")
        return recipe.as_dict()

class RecipesList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', required=False, type=str, location='args')
        self.reqparse.add_argument('is_calibration_recipe', required=False, type=str, location='args')
        super(RecipesList, self).__init__()

    @auth.login_required
    def get(self):
        session = Session()
        params = self.reqparse.parse_args()

        if params['is_calibration_recipe'] is not None:
            if params['is_calibration_recipe']:
                recipes = session.query(Recipe).join(RecipeTag).join(Tag).filter(Tag.name == 'calibration').all()
            else:
                recipes = session.query(Recipe).join(RecipeTag).join(Tag).filter(Tag.name != 'calibration').all()
            return (my_map(lambda r: r.as_dict(), recipes))
        if params['name'] is not None:
            recipes = session.query(Recipe).filter(Recipe.name.ilike('%' + str(params['name']) + '%')).all()
            return (my_map(lambda r: r.as_dict(), recipes))

        recipes = session.query(Recipe).all()
        return (my_map(lambda r: r.as_dict(), recipes))

class EntityRecipes(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('recipe_pk', required=True, type=int, location='json')
        self.reqparse.add_argument('rating', required=False, type=int, location='json')
        self.reqparse.add_argument('is_calibration_recipe', required=False, type=bool, location='json')
        self.reqparse.add_argument('notes', required=False, type=str, location='json')
        self.reqparse.add_argument('entity_pk', required=True, type=int, location='json')
        super(EntityRecipes, self).__init__()

    @auth.login_required
    def post(self):
        recipe_rating = self.reqparse.parse_args()
        #insert using request body params
        #return recipe rating json object

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

        return my_map(lambda e: e.as_dict(), entities)

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

        return (entity_dict)

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

        if params['allergies'] is not None:
            allergies = params['allergies']

            for allergy in allergies:
                ingredient = None
                if isinstance(allergy, basestring):
                    allergy = allergy.lower().strip(' ')
                    ingredient = session.query(Ingredient).filter_by(name = allergy).first()
                elif isinstance(allergy, int):
                    ingredient = session.query(Ingredient).filter_by(ingredient_pk = allergy).first()
                else:
                    abort(400, "Allergy must be an integer or a string.")

                if ingredient is None:
                    abort(400, "Allergy, " + str(ingredient) + ", does not exist.")

                if ingredient.ingredient_pk not in my_map(lambda a: a.ingredient_fk, entity.allergies):
                    # if this entity doesn't have this dietary concern, add the dietary concern
                    allergy = Allergy(entity_fk = entity.entity_pk, ingredient_fk = ingredient.ingredient_pk)
                    session.add(allergy)

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

                if tag.tag_pk not in my_map(lambda t: t.tag_fk, entity.entity_tags):
                    # if this entity doesn't have this dietary concern, add the dietary concern
                    entity_tag = EntityTag(entity_fk = entity.entity_pk, tag_fk = tag.tag_pk)
                    session.add(entity_tag)

        session.commit()

        return my_map_to_list(entity.as_dict())

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

        return (entity.as_dict())

class Tokens(Resource):
    @auth.login_required
    def get(self):
        token = g.entity.generate_auth_token(60000) # expires after 16.6 hours
        return { 'token': token.decode('ascii') }

    @auth.login_required
    def delete(self):
        #TODO store token in db and upon logout invalidate row
        pass

class TagsList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tag_type')
        super(TagsList, self).__init__()

    @auth.login_required
    def get(self, tag_type_pk):
        session = Session()
        tags = session.query(Tag).filter_by(tag_type_fk = tag_type_pk).all()
        return (my_map(lambda t: t.as_dict(), tags))

class EntityMealPlans(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('date', required = False, type=str)
        super(EntityMealPlans, self).__init__()

    @auth.login_required
    @validate_access
    def get(self, entity_pk):
        import time
        params = self.reqparse.parse_args()
        date = params['date']

        session = Session()

        if date is None:
            # default to current date
            date = time.strftime("%Y-%m-%d")

        meal_plans = session.query(MealPlan).filter(MealPlan.entity_fk == entity_pk,  MealPlan.eat_on == date).all()

        if meal_plans is None:
            return None

        meal_plan_dict = {}

        for meal_plan in meal_plans:
            if meal_plan.meal_type not in meal_plan_dict:
                meal_plan_dict[meal_plan.meal_type] = []
            meal_plan_dict[meal_plan.meal_type] = my_map_to_list(meal_plan.as_dict())

        return meal_plan_dict

    @auth.login_required
    def post(self, entity_pk):
        #call algorithm
        #return error for problem, otherwise return None
        pass

class TagsList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tag_type_pk', required = False, type=int)
        self.reqparse.add_argument('tag_type_name', required = False, type=str)
        super(TagsList, self).__init__()

    @auth.login_required
    def get(self):
        params = self.reqparse.parse_args()
        tag_type_pk = params['tag_type_pk']
        tag_type_name = params['tag_type_name']
        session = Session()
        return 'asf'

'''
        print ""
        print "params", params
        print ""

        tags = None
        if tag_type_pk is not None:
            tags = session.query(Tag).filter_by(tag_type_fk = tag_type_pk).all()
        elif tag_type_name is not None:
            tags = session.query(Tag).filter(tag.tag_type.tag_type_pk == tag_type_pk).all()
        else:
            tags = session.query(Tag).all()

        print ""
        print(tags)
        print ""
        return my_map(lambda tag: tag.as_dist(), tags)
'''

my_api.add_resource(TagsList, '/api/v2.0/tag_types/<int:tag_type_pk>/tags', endpoint = 'tagslist')

my_api.add_resource(EntitiesList, '/api/v2.0/entities', endpoint = 'entitieslist')
my_api.add_resource(Entities, '/api/v2.0/entities/<int:entity_pk>', endpoint = 'entities')
my_api.add_resource(EntityMealPlans, '/api/v2.0/entities/<int:entity_pk>/meal_plans', endpoint = 'entitymealplans')

my_api.add_resource(RecipesList, '/api/v2.0/recipes', endpoint = 'recipeslist')
my_api.add_resource(Recipes, '/api/v2.0/recipes/<int:recipe_pk>', endpoint ='recipes')
my_api.add_resource(EntityRecipes, '/api/v2.0/entities/<int:entity_pk>/recipes/<int:recipe_pk>', endpoint = 'entityrecipes')

my_api.add_resource(Tokens, '/api/v2.0/tokens', endpoint = 'tokens')

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
