from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

###################################
#### Setup the flask app object ####
###################################

app = Flask(__name__)

# read from password file
try:
    lines = [line.rstrip('\n') for line in open(dir_path + '.secret_key')]
    secret_key = lines[0]
except Exception, exception:
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
except Exception, exception:
    sys.exit("Couldn't get database config files. Does .db_config exist?")

engine = create_engine('postgresql://' + user + ':' + password + '@' + host + '/' + database, echo=True)
Session = sessionmaker(bind=engine)

import api.routes
