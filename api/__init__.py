from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import Pool, NullPool
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

###################################
#### Setup the flask app object ####
###################################

app = Flask(__name__, static_url_path="")

# read from password file
try:
    lines = [line.rstrip('\n') for line in open(dir_path + '.secret_key')]
    secret_key = lines[0]
except Exception as exception:
    sys.exit("Couldn't get secret key. Does .secret_key exist?")

app.config['DEBUG'] = True
app.secret_key = secret_key

##################################################
#### Setup SQLAlchemy Engine and Session Maker####
##################################################

# read from database config file to get correct settings for connecting the to db
try:
    lines = [line.rstrip('\n') for line in open(dir_path + '.db_config')]
    user, password, host, database = lines
except Exception as exception:
    sys.exit("Couldn't get database config files. Does .db_config exist?")

# use NullPool to avoid idle transactions on postgres
# set autocommit to true
engine = create_engine('postgresql://' + user + ':' + password + '@' + host + '/' + database, echo=False, poolclass=NullPool)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

# handle close and rolling back sessions
@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception and session.is_active:
        print("EXCEPTION: " + str(exception))
        session.rollback()

    session.remove()

import api.routes
