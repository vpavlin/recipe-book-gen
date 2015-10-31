import os
import json
import copy
import uuid

template_str = """
[
  {
    "lang": "lang",
    "translate_to": "lang",
    "title": "Title of the book",
    "id": "uuid",
    "data": [
      {
        "country": "Country",
        "recipes": [
          {
            "id": "uuid",
            "title": {
              "data": "Title of the recipe",
              "modified": 0
            },
            "description": {
              "data": "Description of the food.",
              "modified": 0
            },
            "image": {
              "uri": "link_to_the_image",
              "description": {
                "data": "Image description",
                "modified": 0
              }
            },
            "serving": "Serving",
            "preparing_time": "Preparing time",
            "ingredients": [
              "List",
              "of",
              "Ingredients"
            ],
            "directions": {
              "data": "Directions for recipe",
              "modified": 0,
              "appended_to_docs": 0
            },
            "done": 0
          }
        ]
      }
    ]
  }
]

"""

class DataStorage(object):
    path = "data/recipes.json"
    content = []
    def __init__(self):
        print("Using file: %s/%s", os.getcwd(), self.path)
        try:
            with open(self.path, "r") as fp:
                self.content = json.load(fp)
        except:
            pass



    def find_recipe(self, uuid):
        for book in self.content:
            for country in book["data"]:
                for recipe in country["recipes"]:
                    print(recipe["uuid"])
                    if uuid == recipe["uuid"]:
                        return recipe, country

    def update(self, data):
        to_update = None
        new = True

        if len(self.content) == 0:
            self.generate_empty(data)
            return

        for book in self.content:
            if data["book_uuid"] == book["uuid"]:
                for country in book["data"]:
                    print(country["country"])
                    if data["country"] == country["country"]:
                        for recipe in country["recipes"]:
                            if data["uuid"] == recipe["uuid"]:
                                to_update = recipe

                        tmp = copy.deepcopy(data)
                        del(tmp["book_uuid"])
                        del(tmp["country"])
                        print(to_update)
                        if to_update:
                            new = False
                            country["recipes"].remove(to_update)

                        country["recipes"].append(tmp)
                        return new
        return False


    def generate_empty(self, data):
        template = json.loads(template_str)

        self.content = template
        self.content[0]["uuid"] = data["book_uuid"] if data.get("book_uuid") else str(uuid.uuid4())
        print(data)
        self.content[0]["data"][0]["country"] = data["country"]
        tmp = copy.deepcopy(data)
        del(tmp["book_uuid"])
        del(tmp["country"])
        if tmp.get("title"):
            self.content[0]["data"][0]["recipes"][0] = tmp
        else:
            self.content[0]["data"][0]["recipes"] = []

    def save(self):
        with open(self.path, "w") as fp:
            json.dump(self.content, fp)

    def add_country(self, book_uuid, country):
        if len(self.content) == 0:
            self.generate_empty({"country": country, "book_uuid":book_uuid})
            return True


        for book in self.content:
            if book_uuid == book["uuid"]:
                for c in book["data"]:
                    if c.get("country") == country:
                        return False

                book["data"].append({"country": country, "recipes": []})
        return True

    def get_all(self):
        recipe_t = {"title": "", "uuid": ""}
        data_t = {"country": "", "recipes": []}
        book_t = {"title": "", "uuid": "", "data": [] }
        result = []
        for book in self.content:
            tmp = copy.deepcopy(book_t)
            tmp["title"] = book["title"]
            tmp["uuid"] = book["uuid"]
            for country in book["data"]:
                tmp2 = copy.deepcopy(data_t)
                tmp2["country"] = country["country"]
                for recipe in country["recipes"]:
                    tmp3 = copy.deepcopy(recipe_t)
                    tmp3["title"] = recipe["title"]
                    tmp3["uuid"] = recipe["uuid"]
                    tmp2["recipes"].append(tmp3)
                result.append(tmp2) #FIXME
            #result.append(tmp)

        return result

    def delete_recipe(self, uuid):
        recipe, country = self.find_recipe(uuid)
        country["recipes"].remove(recipe)
