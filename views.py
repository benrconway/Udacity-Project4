# Here I will write the Flask server part of the application
from models import Base, User
from flask import Flask, jsonify, request, url_for, abort, g, render_template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

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
@app.route('/catalogue', methods=['GET', 'POST'])
@app.route('/catalogue/<int:catalogue_id>/', methods=['GET', 'PUT', 'DELETE'])
@app.route('/catalogue/<int:catalogue_id>/items', methods=['GET', 'POST'])
@app.route('/catalogue/<int:catalogue_id>/items/<int:item_id>/', methods=['GET', 'PUT', 'DELETE'])

@app.route('/api/catalogue/all')
def apiMain():
    catalogues = session.query(Catalogues).all()
    items = session.query(Items).all()
    return jsonify(Catalogues=[catalog.serialize for catalog in catalogues],
        Items=[item.serialize for item in items])


# Maybe don't need this one
# @app.route('/api/catalogue/<int:catalogue_id>')
# def apiCatalogueItems():


@app.route('/api/catalogue/<int:catalogue_id>/items')
def catalogueAndItems():
    catalogue = session.query(Catalogues).filter_by(id=catalogue_id).one()
    items = session.query(Items).filter_by(catalogue_id=catalogue_id).all()
    return jsonify(Catalogues=[catalogue.serialize],
        Items=[item.serialize for item in items])


@app.route('/api/catalogue/<int:catalogue_id>/items/<int:item_id>')
def singleItem():
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(Items=[item.serialize])
