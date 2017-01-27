"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, jsonify, abort, make_response, request
app = Flask(__name__)

entities = []
#    entity : '',
#    email : '',
#    username : '',
#    password : '',
#    first_name : '',
#    last_name : '',
#    logged_in : False
#}

@app.route( '/api/login', methods=['POST'] )
def login():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)

    entity = _find_entity( request.json['email'], request.json['password'] )
    if( entity is not None ):
        entity['logged_in'] = True
        return jsonify({'status': True})
    else:
        return jsonify({'status': False})

def _find_entity( email, password ):
    matching_entity = filter(
        lambda entity: entity['email'] == email and entity['password'] == password,
        entities
    )

    if len( matching_entity ) > 0:
        return matching_entity[0]

    return None

@app.route( '/api/register', methods=['POST'] )
def register():
    if( not request.json
    or not 'email' in request.json
    or not 'username' in request.json
    or not 'password' in request.json
    or not 'firstName' in request.json
    or not 'lastName' in request.json
    or not 'password' in request.json ):
        abort(400)

    email = request.json['email']
    username = request.json['username']

    matching_entities = filter(
        lambda entity: entity['email'] == email or entity['email'] == email,
        entities
    )

    if len( matching_entities ) > 0:
        abort(400)

    entities.append({
        'email' : email,
        'username' : username,
        'password' : request.json['password'],
        'first_name' : request.json['firstName'],
        'last_name' : request.json['lastName'],
        'logged_in' : False
    })

    return jsonify({'status': True})

@app.route( '/api/entities', methods=['GET']  )
def get_entities():
    return jsonify({ 'entities': entities })

@app.errorhandler(400)
def page_not_found(e):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return make_response(jsonify({'error': 'Unexpected Error'}), 500)
