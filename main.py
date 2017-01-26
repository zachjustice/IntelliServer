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
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    if( _validate_login( request.json['username'], request.json['password'] ) ):
        return jsonify({'status': True})
    else:
        return jsonify({'status': False})

def _validate_login( username, password ):
    for entity in entities:
        if username == entity['username'] and entity['password'] == password:
            return True
    return False

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
    conflicting_entities = filter(
        lambda entity: entity['email'] == email or entity['username'] == username,
        entities
    )

    if len( conflicting_entities ) > 0:
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
