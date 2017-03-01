from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from api import secret_key, Session

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

    entity_tags = relationship("EntityTag", back_populates="entity")
    meal_plans = relationship("MealPlan", back_populates="entity")

    def __repr__(self):
        return "<User(entity_pk=%s, username='%s', first_name='%s', last_name='%s', is_admin='%s', email='%s')>" % (self.entity_pk, self.username, self.first_name, self.last_name, self.is_admin, self.email)

    def as_dict(self):
        dietary_concern_tags = filter(lambda entity_tag: entity_tag.tag.tag_type_fk == 1, self.entity_tags)
        dietary_concern_tags = map(lambda entity_tag: entity_tag.tag.as_dict(), dietary_concern_tags) 

        return {
            'entity_pk' : self.entity_pk,
            'username' : self.username,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'email' : self.email,
            'dietary_concerns' : dietary_concern_tags
        }

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({ 'entity_pk': self.entity_pk })

    @staticmethod
    def verify_auth_token(token):
        session = Session()
        s = Serializer(secret_key)

        try:
            data = s.loads(token) # data stores encrypted entity pk
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token

        entity = session.query(Entity).filter_by(entity_pk=data['entity_pk']).first()
        return entity

class EntityTag(Base):
    __tablename__ = 'tb_entity_tag'

    entity_tag_pk = Column("entity_tag", Integer, primary_key=True)
    entity_fk = Column("entity", Integer, ForeignKey('tb_entity.entity'))
    tag_fk = Column("tag", Integer, ForeignKey('tb_tag.tag'))

    tag = relationship("Tag", back_populates="entity_tags")
    entity = relationship("Entity", back_populates="entity_tags")

    def __repr__(self):
        return "<EntityTag(entity_tag ='%s' entity='%s', tag='%s')>" % ( self.entity_tag_pk, self.entity_fk, self.tag_fk )

class Tag(Base):
    __tablename__ = 'tb_tag'

    tag_pk = Column("tag", Integer, primary_key=True)
    tag_type_fk = Column("tag_type", Integer, ForeignKey('tb_tag_type.tag_type'))
    name = Column(String)

    entity_tags = relationship("EntityTag", back_populates="tag")

    def __repr__(self):
        return "<Tag(tag_pk=%s, tag_type_fk=%s, name='%s')>" % (self.tag_pk, self.tag_type_fk, self.name)

    def as_dict(self):
        return {
            'tag_pk' : self.tag_pk,
            'tag_type_fk' : self.tag_type_fk,
            'name' : self.name
        }

class Recipe(Base):
     __tablename__ = 'tb_recipe'

     recipe = Column(Integer, primary_key=True)
     name = Column(String)
     instructions = Column(String)
     description = Column(String)
     preparation_time = Column(Integer)

     meal_plans = relationship("MealPlan", back_populates="recipe")

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

class MealPlan(Base):
    __tablename__ = 'tb_meal_plan'

    meal_plan_pk = Column('meal_plan', Integer, primary_key=True)
    entity_fk = Column('entity', Integer, ForeignKey('tb_entity.entity'), nullable=False)
    recipe_fk = Column('recipe', Integer, ForeignKey('tb_recipe.recipe'), nullable=False)
    meal_type = Column(String, nullable=False)
    eat_on = Column(String, nullable=False)

    recipe = relationship("Recipe", back_populates="meal_plans")
    entity = relationship("Entity", back_populates="meal_plans")

    def as_dict(self):
        return {
            'meal_plan_pk' : self.meal_plan_pk,
            'entity_fk' : self.entity_fk,
            'recipe_fk' : self.recipe_fk,
            'meal_type' : self.meal_type
        }
