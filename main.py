"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, jsonify
app = Flask(__name__)

entity = {
    'username' : 'skim870',
    'email_address' : 'bbjelly@gmail.com'
}

@app.route( '/login/<int:username>', methods=['GET'] )
def get():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    if( validate_login( request.username, request.password ) ):
        return jsonify({'status': True})
    else:
        return jsonify({'status': False})

def validate_login( username, password ):
    return True

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return make_response(jsonify({'error': 'Unexpected Error'}), 500)
