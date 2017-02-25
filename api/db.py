from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from main import app
import sys

# read from password file 
try:
    lines = [line.rstrip('\n') for line in open('.password')]
    user, password, host, database = lines
except Exception, exception:
    sys.exit("couldn't get password or username")

engine = create_engine('postgresql://' + user + ':' + password + '@' + host + '/' + database, echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Entity(Base):
     __tablename__ = 'tb_entity'

     entity_pk = Column("entity", Integer, primary_key=True)
     username = Column(String)
     first_name = Column(String)
     last_name = Column(String)
     password = Column(String)
     is_admin = Column(Boolean, default=False)
     email = Column(String)

     def __repr__(self):
        return "<User(entity_pk=%s, username='%s', first_name='%s', last_name='%s', is_admin='%s', email='%s')>" % (self.entity_pk, self.username, self.first_name, self.last_name, self.is_admin, self.email)

     def as_dict(self):
        return {
            'entity_pk' : self.entity_pk,
            'username' : self.username,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'email' : self.email
        }

     def hash_password(self, password):
         self.password = pwd_context.encrypt(password)

     def verify_password(self, password):
         return pwd_context.verify(password, self.password)

     def generate_auth_token(self, expiration = 600):
         s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
         return s.dumps({ 'entity_pk': self.entity_pk })

     @staticmethod
     def verify_auth_token(token):
         session = Session()
         s = Serializer(app.config['SECRET_KEY'])
         try:
             data = s.loads(token) # data stores encrypted entity pk
         except SignatureExpired:
             return None # valid token, but expired
         except BadSignature:
             return None # invalid token
         entity = session.query(Entity).filter_by(entity_pk=data['entity_pk']).first()
         return entity

class Recipe(Base):
     __tablename__ = 'tb_recipe'

     recipe = Column(Integer, primary_key=True)
     name = Column(String)
     instructions = Column(String)
     description = Column(String)
     preparation_time = Column(Integer)

     def __repr__(self):
        return "<Recipe(recipe ='%s' name='%s', description='%s', preparation_time='%s')>" % ( self.recipe, self.name, self.description, self.preparation_time)

     def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class RecipeTag(Base):
     __tablename__ = 'tb_recipe_tag'

     recipe_tag = Column(Integer, primary_key=True)
     recipe = Column(Integer)
     tag = Column(Integer)

     def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

     def __repr__(self):
        return "<Recipe(recipe ='%s' name='%s', description='%s', preparation_time='%s')>" % ( self.recipe, self.name, self.description, self.preparation_time)
