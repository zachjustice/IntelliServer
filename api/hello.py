from bottle import route, run

from bottle import route, run

@route('/hello')
def hello():
        return "<h1>What up!</h1>"

run(host='gae')

