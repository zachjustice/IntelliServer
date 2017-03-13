from recipe_scrapers import scrap_me
import urllib.request as urllib2
import time
import re

def scrape_data(url):
    try:
        return scrap_me(url)
    except urllib2.HTTPError:
        print("Retrying because requests exceeded")
        time.sleep(5)
        return scrape_data(url)

def parse_recipes(urls, categoryTags):
    recipeList = []
    for url in urls:
        print ("Getting Recipe for " + str(url))
        #web-scrape
        data = scrape_data(url)
        recipeName = data.title()
        recipeTime = int(data.prepTime())
        recipeDescription = data.description()
        recipeIngredients = data.ingredients()
        recipeInstructions = data.instructions()
        recipeImage = data.imageUrl()

        #clean-up
        recipeInstructions =  '\n'.join([remove_ads(i) for i in recipeInstructions.split('\n')])
        recipeIngredients = [parse_ingredient(remove_ads(i)) for i in recipeIngredients]
        recipeIngredients = [x for x in recipeIngredients if x is not None]

        #storage
        recipeList.append(Recipe(recipeName, recipeDescription, recipeInstructions, recipeTime, recipeIngredients, categoryTags, recipeImage))

    #to store into DB
    #ingredientList = find_unique_ingredients(recipeList)
    return recipeList


def remove_ads(string):
    remove_list = ['ADVERTISEMENT']
    word_list = string.split()
    return ' '.join([i for i in word_list if i not in remove_list])

def parse_ingredient(string):
    #set-up keyword lists
    unitWords = ['inch', 'cups', 'slices', 'packs', 'packages', 'tablespoons', 'teaspoons', 'pounds', 'quarts', 'pints', 'cc', 'cm', 'ounces', 'oz', 'liters', 'kilograms', 'grams', 'sticks', 'cloves', 'pinches', 'halves']
    descWords = ['sliced', 'chopped', 'shredded', 'minced', 'diced', 'canned', 'crushed', 'ground', 'softened', 'melted', 'separated', 'divided', 'cooked', 'uncooked', 'peeled', 'optional', 'boneless', 'skinless']
    adverbs = ['finely', 'well', 'carefully', 'thinly']
    stopWords = ['and', 'or', 'a', 'to', 'taste']

    #initialize fields
    name = ''
    quantity = ''
    unit = ''
    description = ''

    #strip alpha-numeric
    string = re.sub('[^0-9a-zA-Z/]', ' ', string)
    string = string.lower()

    words = string.split()
    for word in words:
        if any(word in x for x in stopWords):
            continue
        if has_numbers(word):
            quantity += (word + ' ')
        elif any(word in x for x in descWords) or any(word in x for x in adverbs):
            description += (word + ' ')
        elif any(word in x for x in unitWords) and word not in unit:
            unit += word + ' '
        else:
            name += word + ' '

    #add defaults
    if not quantity:
        quantity = '1'
    if not unit:
        unit = 'item(s)'
    if not description:
        description = 'none'
    if not name:
       return None

    #post processing
    name = name.strip()
    quantity = quantity.strip()
    unit = unit.strip()
    description = description.strip()

    #add full-length description
    description = string.strip()

    return Ingredient(name, quantity, unit, description)

def has_numbers(string):
    return any(char.isdigit() for char in string)

def find_unique_ingredients(recipeList):
    aggregate = []
    names = []
    for r in recipeList:
        for i in r.ingredients:
            if i.name not in names:
                aggregate.append(i)
                names.append(i.name)
    return aggregate

class Recipe:
    def __init__(self, name, description, instructions, preparationTime, ingredients, categoryTags, imageUrl):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.preparationTime = preparationTime
        self.ingredients = ingredients
        self.recipePk = None
        self.tags = self.generate_tags()
        self.categoryTags = categoryTags
        self.imageUrl = imageUrl
        for tag in categoryTags:
            self.tags.append(tag)

    def generate_tags(self):
        tags = {'gluten-free': ['barley', 'bread', 'bulgur', 'couscous', 'gluten', 'farina', 'flour', 'malt', 'rye', 'semolina', 'spelt', 'triticale', 'wheat', 'wheat germ'],
    'pescatarian': ['bacon', 'beef', 'boar', 'breast', 'chicken', 'duck', 'ham', 'horse', 'intestine', 'kangaroo', 'lamb', 'mutton', 'partridge', 'pork', 'porkchop', 'poultry', 'quail', 'rabbit', 'tripe', 'turkey'],
    'vegetarian': ['anchovy', 'bass', 'catfish', 'caviar', 'clams', 'crab', 'fish', 'lobster', 'mackerel', 'meat', 'mussel', 'octopus', 'oyster', 'prawn', 'salmon', 'sardines', 'shellfish', 'shrimp', 'squid', 'swordfish', 'tilefish', 'trout', 'tuna', 'whitefish', 'worcestershire','bacon', 'beef', 'boar', 'breast', 'chicken', 'duck', 'ham', 'horse', 'intestine', 'kangaroo', 'lamb', 'mutton', 'partridge', 'pork', 'porkchop', 'poultry', 'quail', 'rabbit', 'tripe', 'turkey'],
    'vegan': ['cheese', 'yogurt', 'cream', 'gelatin', 'gummy', 'sour cream', 'marshmallow', 'anchovy', 'bass', 'catfish', 'caviar', 'clams', 'crab', 'fish', 'lobster', 'mackerel', 'meat', 'mussel', 'octopus', 'oyster', 'prawn', 'salmon', 'sardines', 'shellfish', 'shrimp', 'squid', 'swordfish', 'tilefish', 'trout', 'tuna', 'whitefish', 'worcestershire','bacon', 'beef', 'boar', 'breast', 'chicken', 'duck', 'ham', 'horse', 'intestine', 'kangaroo', 'lamb', 'mutton', 'partridge', 'pork', 'porkchop', 'poultry', 'quail', 'rabbit', 'tripe', 'turkey']}

        recipeTags = []

        for tag in tags.keys():
            notContains = True
            for ingredient in self.ingredients:
                for item in tags[tag]:
                    if item in ingredient.name:
                        notContains = False
            if notContains:
                recipeTags.append(tag)
        if not recipeTags:
            return []
        return recipeTags


class Ingredient:
    def __init__(self, name, quantity, unit, description):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.description = description
        self.ingredientPk = None
