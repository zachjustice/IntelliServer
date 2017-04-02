from ._abstract import AbstractScraper
from ._utils import get_minutes, normalize_string


class AllRecipes(AbstractScraper):

    @classmethod
    def host(self):
        return 'allrecipes.com'

    def title(self):
        return self.soup.find('h1').get_text()

    def description(self):
        return self.soup.find('div', {'class': 'submitter__description'}).get_text()

    def prepTime(self):
        return get_minutes(self.soup.find('span', {'class': 'ready-in-time'}))

    def ingredients(self):
        ingredients_html = self.soup.findAll('li', {'class': "checkList__line"})

        return [
            normalize_string(ingredient.get_text())
            for ingredient in ingredients_html
            if ingredient.get_text(strip=True) not in ('Add all ingredients to list', '')
        ]

    def instructions(self):
        instructions_html = self.soup.findAll('span', {'class': 'recipe-directions__list--item'})

        store = '\n'.join([
            normalize_string(instruction.get_text())
            for instruction in instructions_html
        ])
        return store

    def imageUrl(self):
        out = self.soup.find(itemprop='image')['src']
        return out

    def nutrition_info(self):
        nutrition_dict = {}

        servings = self.soup.find(itemprop='recipeYield')['content']
        nutrition_dict['servings'] = str(servings)

        calories = self.soup.find(itemprop='calories')
        if calories is not None:
            calories = calories.get_text()
        nutrition_dict['calories'] = str(calories)

        fat = self.soup.find(itemprop='fatContent')
        if fat is not None:
            fat = fat.get_text()
        nutrition_dict['fat'] = str(fat)

        protein = self.soup.find(itemprop='proteinContent')
        if protein is not None:
            protein = protein.get_text()
        nutrition_dict['protein'] = str(protein)

        cholesterol = self.soup.find(itemprop='cholesterolContent')
        if cholesterol is not None:
            cholesterol = cholesterol.get_text()
        nutrition_dict['cholesterol'] = str(cholesterol)

        sodium = self.soup.find(itemprop='sodiumContent')
        if sodium is not None:
            sodium = sodium.get_text()
        nutrition_dict['sodium'] = str(sodium)

        carbs = self.soup.find(itemprop='carbohydrateContent')
        if carbs is not None:
            carbs = carbs.get_text()
        nutrition_dict['carbs'] = str(carbs)
        return nutrition_dict



