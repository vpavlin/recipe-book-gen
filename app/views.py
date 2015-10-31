from flask import render_template, request
from flask import jsonify
from app import app
import os
import requests
import json
import uuid
import copy
from ds import DataStorage


@app.route('/')
@app.route('/index')
def index():
    ds = DataStorage()
    all = ds.get_all()
    print(all)
    return render_template("index.html", title = "title", all = all)

@app.route('/saveRecipe', methods=['POST'])
def save_recipe():
    ds = DataStorage()
    new = ds.update(json.loads(request.json))
    ds.save()

    return jsonify({"was_new":new, "recipe": request.json})

@app.route('/getUUID')
def get_uuid():
    return str(uuid.uuid4())

@app.route('/getRecipe/<uuid>')
def get_recipe(uuid):
    ds = DataStorage()
    r, country = ds.find_recipe(uuid)
    r["country"] = country["country"]
    return json.dumps(r)

@app.route('/newCountry/<book_uuid>/<country>')
def new_country(book_uuid, country):
    ds = DataStorage()
    if ds.add_country(book_uuid, country):
        ds.save()
    else:
        print("Failed")

    return country

@app.route('/deleteRecipe/<uuid>')
def delete_recipe(uuid):
    ds = DataStorage()
    res = ds.delete_recipe(uuid)
    ds.save()

    return uuid

@app.context_processor
def utility_processor():
    def sc(country):
        return country.replace(" ", "-")
    return dict(sc=sc)
