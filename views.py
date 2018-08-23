from models import Base, Users, Categories, Items
from flask import Flask, jsonify, request, redirect, url_for, abort, flash, g, render_template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask import session as login_session

from flask.ext.httpauth import HTTPBasicAuth
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///itemcatalogue.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

# @app.route('/users', methods=['POST'])
#
# @app.route('/login')
# @app.route('/oauth/<string:provider>', methods=['POST'])
# @app.route('/token')

@app.route('/')
@app.route('/categories/')
def home():
    categories = session.query(Categories).all()
    category = Categories()
    items = session.query(Items).all()
    return render_template('categories.html', categories=categories, items=items, category=category)

@app.route('/categories/<string:category_name>/')
@app.route('/categories/<string:category_name>/items')
def showOneCategoryAndItems(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    return render_template('singleCategory.html', category=category, items=items)

@app.route('/categories/<string:category_name>/items/new', methods=['GET', 'POST'])
def newItem(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        url = request.form['url']
        item = Items(name=name, description=description, location=location, url=url, category=category)
        session.add(item)
        session.commit()
        # TODO: Add user from login_session
        flash("{0} has been added to {1}.".format(item.name, category.name))
        return redirect(url_for('showOneCategoryAndItems', category_name=category_name))

    else:
        return render_template('newItem.html', category=category)


@app.route('/categories/<string:category_name>/items/<int:item_id>/', methods=['GET', 'PUT', 'DELETE'])
def singleItem(category_name, item_id):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    if request.method =='PUT':
        updatedItem = updateItem(request.form, item)
        session.add(updatedItem)
        session.commit()
        flash("Changes have been successfully made to {0}.".format(item.name))
        return redirect(url_for('showOneCategoryAndItems', category_name=category_name))

    elif request.method == 'DELETE':
        session.delete(item)
        session.commit()
        flash("{0} has been deleted from {1}.".format(item.name, category.name))
        return redirect(url_for('showOneCategoryAndItems', category_name=category_name))

    else:
        return render_template('singleItem.html', category=category, item=item)

@app.route('/categories/<string:category_name>/items/<int:item_id>/edit')
def editItem(category_name, item_id):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    return render_template('editItem.html', category=category, item=item)

@app.route('/categories/<string:category_name>/items/<int:item_id>/delete')
def deleteItem(category_name, item_id):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    return render_template('deleteItem.html', category=category, item=item)

# Api routes
@app.route('/api/categories/')
def apiMain():
    categories = session.query(Categories).all()
    items = session.query(Items).all()
    return jsonify(Categories=[catalog.serialize for catalog in catalogues],
        Items=[item.serialize for item in items])

@app.route('/api/categories/<string:category_name>/items')
def apiCatagoryAndItems(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    return jsonify(Categories=[category.serialize],
        Items=[item.serialize for item in items])


@app.route('/api/categories/<string:category_name>/items/<int:item_id>')
def apiSingleItem(category_name, item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(Items=[item.serialize])

# Helper functions
def updateItem(form, item):
    if form['name']:
        item.name = form['name']
    if form['description']:
        item.description = form['description']
    if form['location']:
        item.location = form['location']
    if form['url']:
        item.url = form['url']
    print item.location
    return item

if __name__ == '__main__':
    app.secret_key = "password"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
