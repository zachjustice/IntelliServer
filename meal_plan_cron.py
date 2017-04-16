import time
from webscraper.db import get_entity_pks
from webscraper.classifier import generate_meal_plan
from api.models import my_map

print("MEAL PLAN UPDATE - " + str(time.strftime("%d/%m/%Y")))
entities = my_map(lambda r: r['entity'], get_entity_pks())
entities = [22]

for entity in entities:
    generate_meal_plan(entity, 7, timeDelta = 0)
    print("Meal Plan successfully generated for entity" + str(entity))


