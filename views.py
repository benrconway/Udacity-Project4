from models import Base, Users, Categories, Items
from flask import Flask, jsonify, request, redirect, url_for, abort, flash, \
    g, render_template, make_response
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

# Load client id for my google oauth
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']


@auth.verify_password
def verifyPassword(identifier, password):
    # Identifier can be a token or a username, verify will suply which it is.
    user_id = User.verifyToken(identifier)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = identifier).first()
        if not user or not user.verifyPassword(password):
            return False
    g.user = user
    return True

@app.route('/oauth2callback')
def returnToHome():
    return redirect(url_for('home'))

@app.route('/oauth/<string:provider>', methods=['POST'])
def loginWithOauth(provider):
    print "Oauth endpoint called"
    print request.data
    oneTimeCode = request.data
    if provider == 'google':
        # If google was the provider, exchange the one time code with google
        # for an access token
        try:
            oauthFlow = flow_from_clientsecrets('client_secret.json', scope='')
            oauthFlow.redirect_uri = 'postmessage'
            userCredentials = oauthFlow.step2_exchange(oneTimeCode)

        except FlowExchangeError:
            return respondWith('Failed to authorize with Google', 401)
        print "Made it past check 1"
        # test token validity
        googleAccessToken = userCredentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}'.format(googleAccessToken)  #NOQA
        googleResult = requests.get(url).json()
        # googleResult = googleResponse.json()

        # ensure there was no error before proceeding.
        if googleResult.get('error') is not None:
            return respondWith(result.get('error'), 500)

        # ensure that the following is true:
        # 1. Token and given user IDs match
        googleId = userCredentials.id_token['sub']
        if googleId != googleResult['user_id']:
            return respondWith("User ID's do not match", 401)

        # # 2. The token is has been collected for this web app
        if googleResult['issued_to'] != CLIENT_ID:
            return respondWith("Token was not issued for this application", 401)


        print "Made it past all other checks"

        userinfoURL = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': googleAccessToken, 'alt':'json'}
        # if it doesn't work, separate request and .json()
        data = requests.get(userinfoURL, params=params).json()

        name = data['name']
        email = data['email']

        # check to see if they already exist.
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            user = Users(name=name, email=email)
            dbAddUpdate(user)

        return redirect(url_for('home'))
    else:
        return respondWith('Unrecoginized Provider', 500)


@app.route('/token')
@auth.login_required
def getAuthToken():
    token = g.user.generateToken()
    return jsonify({'token': token.decode('ascii')})

@app.route('/users', methods=['POST'])
def newUser():
    name = request.form['name']
    password = request.form['password']

    if name is None or password is None:
        return respondWith('Missing arguments', 400)

    if session.query(Users).filter_by(name=name).first() is not None:
        return respondWith('User already exists', 200)

    user = Users(name=name)
    user.hashPassword(password)
    dbAddUpdate(user)
    return jsonify({'name': user.name}), 201


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
@app.route('/categories/')
def home():
    categories = session.query(Categories).all()
    category = Categories()
    items = session.query(Items).all()
    return render_template('categories.html', categories=categories,
                           items=items, category=category)


@app.route('/categories/<string:category_name>/')
@app.route('/categories/<string:category_name>/items')
def showOneCategoryAndItems(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    return render_template('singleCategory.html',
                           category=category, items=items)


@app.route('/categories/<string:category_name>/items/new',
           methods=['GET', 'POST'])
def newItem(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        url = request.form['url']
        item = Items(name=name, description=description, location=location,
                     url=url, category=category)
        dbAddUpdate(item)
        # TODO: Add user from login_session
        flash("{0} has been added to {1}.".format(item.name, category.name))
        return redirect(url_for('showOneCategoryAndItems',
                                category_name=category_name))
    else:
        return render_template('newItem.html', category=category)


@app.route('/categories/<string:category_name>/items/<int:item_id>/')
def singleItem(category_name, item_id):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    return render_template('singleItem.html', category=category, item=item)


@app.route('/categories/<string:category_name>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_id):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.location = request.form['location']
        item.url = request.form['url']
        dbAddUpdate(item)
        flash("Changes have been successfully made to {0}.".format(item.name))
        return redirect(url_for('showOneCategoryAndItems',
                        category_name=category_name))
    else:
        return render_template('editItem.html', category=category, item=item)


@app.route('/categories/<string:category_name>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'POST':
        dbAddUpdate(item)
        flash("{0} has been deleted from {1}.".format(item.name,
                                                      category.name))
        return redirect(url_for('showOneCategoryAndItems',
                                category_name=category_name))
    else:
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

def respondWith(message, code):
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'
    return response

def dbAddUpdate(object):
    session.add(object)
    session.commit()

if __name__ == '__main__':
    app.secret_key = "password"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
