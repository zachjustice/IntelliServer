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

    entity = _get_entity_by_email_and_password( request.json['email'], request.json['password'] )
    if( entity is not None ):
        entity['logged_in'] = True
        return jsonify({'status': True})
    else:
        return jsonify({'status': False})

def _get_entity_by_email_and_password( email, password ):
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
        lambda entity: entity['username'] == username or entity['email'] == email,
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

@app.route( '/api/logout', methods=['PUT'] )
def logout():
    if not request.json or not 'email' in request.json:
        abort(400)

    matching_entity = filter(
        lambda entity: entity['email'] == request.json['email'],
        entities
    )
    
    if len( matching_entity ) != 1:
        abort(400)
    else:
        matching_entity = matching_entity[0]
            
    matching_entity['logged_in'] = False
    return jsonify({'status': True})

@app.route( '/api/remove_account', methods=['DELETE'] )
def remove_account():
    if not request.json or not 'email' in request.json:
        abort(400)

    matching_entity = filter(
        lambda entity: entity['email'] == json.request['email'],
        entities
    )
    
    if len( matching_entity ) != 1:
        abort(400)
    else:
        del entities[entities.index(matching_entity[0])]
        
    return jsonify({'status': True})

@app.errorhandler(400)
def page_not_found(e):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(405)
def application_error(e):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return make_response(jsonify({'error': 'An unexpected error occured'}), 500)
