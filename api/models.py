from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from api import secret_key

Base = declarative_base()

def my_map(f, l):
    new = []
    for i in l:
        new.append(f(i))
    return new

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
    allergies = relationship("Allergy", back_populates="entity")
    meal_plans = relationship("MealPlan", back_populates="entity")

    def __repr__(self):
        return "<User(entity_pk=%s, username='%s', first_name='%s', last_name='%s', is_admin='%s', email='%s')>" % (self.entity_pk, self.username, self.first_name, self.last_name, self.is_admin, self.email)

    def as_dict(self):
        dietary_concern_tags = filter(lambda entity_tag: entity_tag.tag.tag_type_fk == 1, self.entity_tags)
        dietary_concern_tags = my_map(lambda entity_tag: entity_tag.tag.name.as_dict(), dietary_concern_tags)

        allergies = my_map(lambda allergy: allergy.ingredient.name, self.allergies)

        return {
            'entity_pk' : self.entity_pk,
            'username' : self.username,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'email' : self.email,
            'dietary_concerns' : dietary_concern_tags,
            'allergies' : allergies
        }

    def hash_password(self, password):
        self.password = str(pwd_context.encrypt(password))

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({ 'entity_pk': self.entity_pk })

    @staticmethod
    def verify_auth_token(token):
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

class TagType(Base):
    __tablename__ = 'tb_tag_type'

    tag_type_pk = Column("tag_type", Integer, primary_key=True)
    name = Column(String)

    tags = relationship("Tag", back_populates="tag_type")

    def __repr__(self):
        return "<Tag(tag_type_pk=%s, name='%s')>" % (self.tag_pk, self.name)

    def as_dict(self):
        return {
            'tag_pk' : self.tag_pk,
            'name' : self.name
        }

class Tag(Base):
     __tablename__ = 'tb_tag'

     tag_pk = Column("tag", Integer, primary_key=True)
     tag_type_fk = Column("tag_type", Integer, ForeignKey('tb_tag_type.tag_type'))
     name = Column(String)

     entity_tags = relationship("EntityTag", back_populates="tag")
     tag_type    = relationship("TagType", back_populates="tags") # plural bc many to one
     recipe_tags = relationship("RecipeTag", back_populates="tag")

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

     recipe_pk = Column("recipe", Integer, primary_key=True)
     name = Column(String)
     instructions = Column(String)
     description = Column(String)
     preparation_time = Column(Integer)
     image_url = Column(String)

     #nutrition info
     serving_count = Column(String)
     calories = Column(String)
     fat = Column(String)
     protein = Column(String)
     carbs = Column(String)
     cholesterol = Column(String)
     sodium = Column(String)

     nutrition_info = {}

     meal_plans = relationship("MealPlan", back_populates="recipe")
     recipe_tags = relationship("RecipeTag", back_populates="recipe")
     ingredient_recipe = relationship("IngredientRecipe", back_populates="recipe")


     def __repr__(self):
         return "<Recipe(recipe ='%s' name='%s', description='%s', preparation_time='%s', image_url = '%s', nutrition_info = '%s')>" % ( self.recipe_pk,
                self.name, self.description, self.preparation_time, self.image_url, self.nutrition_info)

     def as_dict(self):
         self.nutrition_info['Serving Count'] = self.serving_count
         self.nutrition_info['Calories'] = self.calories
         self.nutrition_info['Protein'] = self.protein
         self.nutrition_info['Carbs'] = self.carbs
         self.nutrition_info['Cholesterol'] = self.cholesterol
         self.nutrition_info['Sodium'] = self.sodium

         recipe_pks = my_map(lambda r: r.ingredient_fk, self.ingredient_recipe)
         ingredients = filter(lambda ingredient_recipe: ingredient_recipe.recipe_fk == self.recipe_pk, self.ingredient_recipe)
         ingredients = my_map(lambda ingredient_recipe: ingredient_recipe.as_dict(), ingredients)
         return {
            "recipe_pk" : self.recipe_pk,
            "name": self.name,
            "instructions":  self.instructions,
            "description": self.description,
            "preparation_time": self.preparation_time,
            "image_url": self.image_url,
            "ingredients" : ingredients,
            "nutrition_info" : self.nutrition_info
            }

class IngredientRecipe(Base):
     __tablename__ = 'tb_ingredient_recipe'

     ingredient_recipe_pk = Column("ingredient_recipe", Integer, primary_key=True)
     recipe_fk = Column("recipe", Integer, ForeignKey('tb_recipe.recipe'))
     ingredient_fk = Column("ingredient", Integer, ForeignKey('tb_ingredient.ingredient'))
     description = Column("description", String)

     recipe = relationship("Recipe", back_populates="ingredient_recipe")
     ingredient = relationship("Ingredient", back_populates="ingredient_recipe")

     def as_dict(self):
        return {
            #"ingredient_recipe_pk": self.ingredient_recipe_pk,
            #"recipe_fk": self.recipe_fk,
            #"ingredient_fk": self.ingredient_fk,
            "ingredient": self.ingredient.name,
            "description": self.description
        }

     def __repr__(self):
        return "<IngredientRecipe(recipe =%s, ingredient=%s recipe_fk=%s, ingredient_fk=%s, description=%s)>" % (self.recipe, self.ingredient, self.recipe_fk, self.ingredient_fk, self.description)

class RecipeTag(Base):
     __tablename__ = 'tb_recipe_tag'

     recipe_tag_pk = Column("recipe_tag", Integer, primary_key=True)
     recipe_fk = Column("recipe", Integer, ForeignKey('tb_recipe.recipe'))
     tag_fk = Column("tag", Integer, ForeignKey('tb_tag.tag'))

     recipe = relationship("Recipe", back_populates="recipe_tags")
     tag = relationship("Tag", back_populates="recipe_tags")

     def as_dict(self):
        return {
            "recipe_tag_pk": self.recipe_tag_pk,
            "recipe_fk": self.recipe_fk,
            "tag_fk": self.tag_fk
        }

     def __repr__(self):
        return "<RecipeTag(recipe=%s recipe_fk=%s, tag_fk=%s)>" % (self.recipe, self.recipe_fk, self.tag_fk)

class EntityRecipeRating(Base):
    __tablename__ = 'tb_entity_recipe_rating'

    entity_recipe_rating_pk = Column("entity_recipe_rating", Integer, primary_key=True)
    entity_fk = Column("entity", Integer, ForeignKey('tb_entity.entity'))
    recipe_fk = Column("recipe", Integer, ForeignKey('tb_recipe.recipe'))
    rating = Column(String)
    is_favorite = Column(Boolean, default=False)
    is_calibration_recipe = Column(Boolean, default=False)
    notes = Column(String)
#
#    recipe = relationship("Recipe", back_populates="entity_recipe_rating")
#    entity = relationship("Entity", back_populates="entity_recipe_rating")
#
    def as_dict(self):
        return {
            'entity_recipe_rating_pk' : self.entity_recipe_rating_pk,
            'entity_fk' : self.entity_fk,
            'recipe_fk' : self.recipe_fk,
            'rating' : self.rating,
            'is_favorite' : self.is_favorite,
            'is_calibration_recipe' : self.is_calibration_recipe,
            'notes' : self.notes
        }

    def __repr__(self):
        return "<EntityRecipeRating(entity_recipe_rating ='%s' entity='%s', recipe='%s', rating='%s', is_favorite='%s', is_calibration_recipe='%s', notes='%s')>" % ( self.entity_recipe_rating_pk, self.entity_fk, self.recipe_fk, self.rating, self.is_favorite, self.is_calibration_recipe, self.notes)

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
        meal_plan = {
            'meal_plan_pk' : self.meal_plan_pk,
            'entity_fk' : self.entity_fk,
            'recipe_fk' : self.recipe_fk,
            'meal_type' : self.meal_type,
            'eat_on' : str(self.eat_on)
        }
        meal_plan.update(self.recipe.as_dict())
        return meal_plan

class Ingredient(Base):
    __tablename__ = 'tb_ingredient'

    ingredient_pk = Column('ingredient', Integer, primary_key=True)
    name = Column('name', String)

    allergies = relationship("Allergy", back_populates="ingredient")
    ingredient_recipe = relationship("IngredientRecipe", back_populates="ingredient")

    def as_dict(self):
        {
            'ingredient_pk' : self.ingredient_pk,
            'name' : self.name
        }

class Allergy(Base):
    __tablename__ = 'tb_allergy'

    allergy_pk = Column('allergy', Integer, primary_key=True)
    entity_fk = Column('entity', Integer, ForeignKey('tb_entity.entity'), nullable=False)
    ingredient_fk = Column('ingredient', Integer, ForeignKey('tb_ingredient.ingredient'), nullable=False)

    ingredient = relationship("Ingredient", back_populates="allergies")
    entity = relationship("Entity", back_populates="allergies")

    def as_dict(self):
        return {
            'entity_fk': self.entity_fk,
            'ingredient_fk' : self.ingredient_fk
        }

