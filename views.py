# Here I will write the Flask server part of the application
from models import Base, User
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

@app.route('/users', methods=['POST'])

@app.route('/login')
@app.route('oauth/<str:provider>', methods=['POST'])
@app.route('/token')
@auth.login_required


@app.route('/')
@app.route('/categories')
def homeRouteHandler():
    categories = session.query(Categories).all()
    items = session.query(Items).all()

    return render_template('home.html', categories=categories, items=items)


@app.route('/categories/<str:category_name>/')
@app.route('/categories/<str:category_name>/items')
def showOneCategoryAndItems():
    categories = session.query(Categories).all()
    category = list(filter(lambda category: category.name = category_name, categories)
    items = session.query(Items).filter_by(category_id=category.id).all()
    return render_template('singleCategory.html', categories=categories, chosen=category, items=items)

@app.route('/categories/<str:category_name>/items/new', methods=['GET', 'POST'])
def newItem():
    category = session.query(Categories).filter_by(name=category_name).one()
    if request.method == 'POST':
        # TODO: create object and store it in the database
        flash("{0} has been added to {1}.".format(item.name, category.name))
        return redirect(url_for('singleCategory.html'))
    else:
        return render_template('newItem.html', category=category)


@app.route('/categories/<str:category_name>/items/<int:item_id>/', methods=['GET', 'PUT', 'DELETE'])
def singleItem():
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    if request.method =='PUT':
        # TODO: Update object in database
        flash("Changes have been successfully made to {0}.".format(item.name))
        return redirect(url_for())
    elif request.method == 'DELETE':
        # TODO: Delete object from database
        flash("{0} has been deleted from {1}.".format(item.name, category.name))
        return redirect(url_for('singleCategory.html'))
    else:
        render_template('singleItem.html', category=category, item=item)

# TODO: add routes for edit and delete pages.

@app.route('/api/categories/')
def apiMain():
    categories = session.query(Categories).all()
    items = session.query(Items).all()
    return jsonify(Categories=[catalog.serialize for catalog in catalogues],
        Items=[item.serialize for item in items])

@app.route('/api/categories/<str:category_name>/items')
def catagoryAndItems():
    category = session.query(Categories).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    return jsonify(Categories=[catalogue.serialize],
        Items=[item.serialize for item in items])


@app.route('/api/category/<str:category_name>/items/<int:item_id>')
def singleItem():
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(Items=[item.serialize])
