# Import the Flask Framework
from flask import Flask, jsonify, abort, make_response, request
app = Flask(__name__)

entities = [
    {
        'email'      : 'admin@intellichef.com',
        'username'   : 'admin',
        'password'   : '5CC',
        'first_name' : 'Intelli',
        'logged_in'  : 'True',
        'last_name'  : 'Chef'
    }
]

@app.route( '/api/login', methods=['POST'] )
def login():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400, 'Email and password must be provided.')

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
        abort(400, 'Registration information is missing.')

    email = request.json['email']
    username = request.json['username']

    matching_entities = filter(
        lambda entity: entity['username'] == username or entity['email'] == email,
        entities
    )

    if len( matching_entities ) > 0:
        return jsonify({'status': True})

    entities.append({
        'email' : email,
        'username' : username,
        'password' : request.json['password'],
        'first_name' : request.json['firstName'],
        'last_name' : request.json['lastName'],
        'logged_in' : True
    })

    return jsonify({'status': True})

@app.route( '/api/entities', methods=['GET']  )
def get_entities():
    return jsonify({ 'entities': entities })

@app.route( '/api/logout', methods=['PUT'] )
def logout():
    if not request.json or not 'email' in request.json:
        abort(400, 'Email must be provided.')

    matching_entity = filter(
        lambda entity: entity['email'] == request.json['email'],
        entities
    )

    if len( matching_entity ) > 1:
        abort(400, 'More than email was found when logging out user.')
    if len( matching_entity ) == 0:
        abort(400, 'This user account does not exist.')
    else:
        matching_entity = matching_entity[0]

    matching_entity['logged_in'] = False
    return jsonify({'status': True})

@app.route( '/api/remove_account', methods=['POST'] )
def remove_account():
    if not request.json or not 'email' in request.json:
        abort(400, 'Email must be provided.')

    matching_entity = filter(
        lambda entity: entity['email'] == request.json['email'],
        entities
    )

    if len( matching_entity ) > 1:
        abort(400, 'More than one email found when removing user account.')
    if len( matching_entity ) == 0:
        abort(400, 'This user account does not exist.')
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
