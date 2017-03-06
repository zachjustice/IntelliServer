CREATE TABLE IF NOT EXISTS tb_entity(
    entity     SERIAL PRIMARY KEY,
    email      VARCHAR(128) UNIQUE NOT NULL,
    username   VARCHAR(128) UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    first_name VARCHAR(128) DEFAULT NULL,
    last_name  VARCHAR(128) DEFAULT NULL,
    is_admin   boolean NOT NULL DEFAULT 'f'
);

CREATE TABLE IF NOT EXISTS tb_recipe(
    recipe           SERIAL PRIMARY KEY,
    name             VARCHAR(128) NOT NULL,
    instructions     TEXT UNIQUE NOT NULL,
    description      TEXT NOT NULL,
    preparation_time INT NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_tag_type(
    tag_type SERIAL PRIMARY KEY,
    name     VARCHAR(128) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_tag(
    tag      SERIAL PRIMARY KEY,
    tag_type INTEGER NOT NULL REFERENCES tb_tag_type( tag_type ),
    name     VARCHAR(128) UNIQUE NOT NULL
);

CREATE UNIQUE INDEX uniq_tag_type_name ON tb_tag(tag_type, name);

CREATE TABLE IF NOT EXISTS tb_entity_tag(
    entity_tag SERIAL PRIMARY KEY,
    entity     INTEGER NOT NULL REFERENCES tb_entity(entity),
    tag        INTEGER NOT NULL REFERENCES tb_tag(tag)
);

CREATE UNIQUE INDEX uniq_entity_tag ON tb_entity_tag(entity, tag);

CREATE TABLE IF NOT EXISTS tb_recipe_tag(
    recipe_tag SERIAL PRIMARY KEY,
    recipe INTEGER REFERENCES tb_recipe( recipe ),
    tag    INTEGER REFERENCES tb_tag   ( tag    )
);

CREATE UNIQUE INDEX uniq_recipe_tag ON tb_recipe_tag(recipe, tag);

CREATE TYPE meal_type AS ENUM('breakfast', 'lunch', 'dinner');

CREATE TABLE IF NOT EXISTS tb_meal_plan(
    meal_plan   SERIAL PRIMARY KEY,
    entity      INTEGER NOT NULL REFERENCES tb_entity( entity ),
    recipe      INTEGER NOT NULL REFERENCES tb_recipe( recipe ),
    eat_on      DATE NOT NULL,
    meal_type   meal_type NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_entity_recipe_rating(
    entity_recipe_rating   SERIAL PRIMARY KEY,
    entity      INTEGER NOT NULL REFERENCES tb_entity( entity ),
    recipe      INTEGER NOT NULL REFERENCES tb_recipe( recipe ),
    rating      INTEGER DEFAULT NULL,
    is_favorite BOOLEAN DEFAULT NULL,
    CONSTRAINT check_valid_rating CHECK( rating >= 0 and rating <= 5 ),
    CONSTRAINT check_rating_or_is_favorite
                CHECK (rating IS NOT NULL or is_favorite IS NOT NULL)
);

CREATE UNIQUE INDEX uniq_entity_recipe_rating ON tb_entity_recipe_rating(entity, recipe);

CREATE TABLE IF NOT EXISTS tb_ingredient(
    ingredient SERIAL PRIMARY KEY,
    name       VARCHAR(128) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_ingredient_recipe(
    ingredient_recipe SERIAL PRIMARY KEY,
    ingredient        INTEGER REFERENCES tb_ingredient( ingredient ),
    recipe            INTEGER REFERENCES tb_recipe( recipe ),
    quantity          VARCHAR(20) DEFAULT NULL,
    unit              VARCHAR(20) DEFAULT NULL,
    description       TEXT DEFAULT NULL,
    preparation_notes TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS tb_allergy(
    allergy    SERIAL PRIMARY KEY,
    entity     INTEGER REFERENCES tb_entity(entity),
    ingredient INTEGER REFERENCES tb_ingredient(ingredient)
);

CREATE UNIQUE INDEX uniq_entity_ingredient ON tb_allergy(entity, ingredient);

INSERT INTO tb_tag_type(name) VALUES ('SYSTEM');
INSERT INTO tb_tag(tag_type, name) VALUES(1, 'calibration');

INSERT INTO tb_tag_type(name) VALUES ('Dietary Concerns');

INSERT INTO tb_tag(name, tag_type) VALUES ('vegetarian', 1);
INSERT INTO tb_tag(name, tag_type) VALUES ('gluten-free', 1);
INSERT INTO tb_tag(name, tag_type) VALUES ('pescatarian', 1);
INSERT INTO tb_tag(name, tag_type) VALUES ('vegan', 1);
