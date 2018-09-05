from models import Base, Users, Categories, Items
from flask import Flask, jsonify, request, redirect, url_for, flash
from flask import session as login_session
from flask import render_template, make_response
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

# Load client id for my google oauth
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

loginLabel = {'login':{
                'name':'Login',
                'action': '/login',
                'style': 'block'
                },
             'logout': {
                'name': 'Logout',
                'action': '/logout',
                'style': 'none;'
                }
            }


@auth.verify_password
def verifyPassword(identifier, password):
    print "Verify Password is called"
    # Identifier can be a token or a username, verify will supply which it is.
    user_id = Users.verifyToken(identifier)
    if user_id:
        user = session.query(Users).filter_by(id = user_id).one()
    else:
        user = session.query(Users).filter_by(name = identifier).first()
        if not user or not user.verifyPassword(password):
            return False
    login_session['user'] = user
    return True

@app.route('/oauth2callback')
def returnToHome():
    return redirect(url_for('home'))

@app.route('/oauth/<string:provider>', methods=['POST'])
def loginWithOauth(provider):
    # print "Oauth endpoint called"
    requestData = json.loads(request.data)
    oneTimeCode = requestData['data']
    if provider == 'google':
        # If google was the provider, exchange the one time code with google
        # for an access token
        try:
            oauthFlow = flow_from_clientsecrets('client_secret.json', scope='')
            oauthFlow.redirect_uri = 'postmessage'
            userCredentials = oauthFlow.step2_exchange(oneTimeCode)

        except FlowExchangeError:
            return respondWith('Failed to authorize with Google', 401)

        # test token validity
        googleAccessToken = userCredentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo'
        params = {'access_token': googleAccessToken }
        googleResult = requests.get(url, params=params).json()

        # ensure there was no error before proceeding.
        if googleResult.get('error') is not None:
            return respondWith(result.get('error'), 500)
        print "This is the access token\n {0}".format(googleAccessToken)
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
        print data
        name = data.get('name', None)
        email = data['email']

        # check to see if they already exist.
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            user = Users(name=name, email=email)
            dbAddUpdate(user)

        login_session['user'] = user
        login_session['provider'] = "google"
        login_session['access'] = googleAccessToken

        return redirect(url_for('home'))
    else:
        return respondWith('Unrecoginized Provider', 500)


@app.route('/users', methods=['GET', 'POST'])
def newUser():

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        if name is None or email is None:
            flash("Something is missing, please check the form and try again.")
            return redirect(url_for('newUser'))

        if session.query(Users).filter_by(name=name).first() is not None:
            flash('That name is already taken, please try another.')
            return redirect(url_for('newUser'))

        user = Users(name=name, email=email)
        user.hashPassword(password)
        dbAddUpdate(user)
        # Get the user back from the DB so that they have an attached ID
        fromDbUser = session.query(Users).filter_by(email=email).one()
        login_session['user'] = fromDbUser
        flash("Welcome {0}, and thank you in advance for all your future \
               contributions.".format(fromDbUser.name))
        return redirect(url_for('home'))
    else:
        return render_template('signup.html', login=loginLabel['login'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Logging in with username and password
    if request.method == 'POST':
        if verifyPassword(request.form['name'], request.form['password']):
            flash("Welcome, {0}!".format(request.form['name']))
            return redirect(url_for('home'))
        else:
            flash("Username and/or Password incorrect. Please try again")
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    if login_session['provider'] == "google":
        googleLogout(login_session['access'])
        login_session['user'] = None
    else:
        login_session['user'] = None

    flash("You have been logged out, we hope you have a lovely day")
    return redirect(url_for('home'))


@app.route('/')
@app.route('/categories/')
def home():
    user = login_session.get('user', None)
    # user = session.merge(user)
    categories = session.query(Categories).all()
    category = Categories()
    items = session.query(Items).all()
    if user is None:
        return render_template('categories.html', categories=categories,
                           items=items, category=category,
                           login=loginLabel['login'])
    else:
        return render_template('categories.html', categories=categories,
                           items=items, category=category,
                           login=loginLabel['logout'])


@app.route('/categories/<string:category_name>/')
@app.route('/categories/<string:category_name>/items')
def showOneCategoryAndItems(category_name):
    user = login_session.get('user', None)

    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    if user is None:
        return render_template('publicSingleCategory.html',
                                category=category, items=items,
                                login=loginLabel['login'])
    else:
        user = session.merge(user)
        return render_template('singleCategory.html',
                               category=category, items=items, user=user,
                               login=loginLabel['logout'])


@app.route('/categories/<string:category_name>/items/new',
           methods=['GET', 'POST'])
def newItem(category_name):
    user = login_session.get('user', None)
    category = session.query(Categories).filter_by(name=category_name).one()
    # User must be logged in to create an item.
    if user is None:
        flash("Sorry, you need to be login to use that.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        url = request.form['url']
        item = Items(name=name, description=description, location=location,
                     url=url, user=user, category=category)
        dbAddUpdate(item)

        flash("{0} has been added to {1}.".format(item.name, category.name))
        return redirect(url_for('showOneCategoryAndItems',
                                category_name=category_name))
    else:
        return render_template('newItem.html', category=category,
                               login=loginLabel['logout'])


@app.route('/categories/<string:category_name>/items/<int:item_id>/')
def singleItem(category_name, item_id):
    user = login_session.get('user', None)
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()

    if user is None:
        return render_template('publicSingleItem.html', category=category,
                                item=item,
                                login=loginLabel['login'])
    else:
        # user = session.merge(user)
        return render_template('singleItem.html', category=category,
                                item=item,
                                login=loginLabel['logout'])


@app.route('/categories/<string:category_name>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_id):
    user = login_session.get('user', None)
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    if user is None:
        flash("Sorry, you need to be login to use that.")
        return redirect(url_for('login'))

    user = session.merge(user)
    if request.method == 'POST':
        # Check IDs match
        if user.id != item.user_id:
            flash("You do not have authority to edit {0}.".format(item.name))
            return redirect(url_for('showOneCategoryAndItems',
                                        category_name=category_name))
        # If they do, update the item.
        item.name = request.form['name']
        item.description = request.form['description']
        item.location = request.form['location']
        item.url = request.form['url']
        dbAddUpdate(item)
        flash("Changes have been successfully made \
              to {0}.".format(item.name))
        return redirect(url_for('showOneCategoryAndItems',
                        category_name=category_name))
    else:
        # Else they are using a GET request.
        return render_template('editItem.html', category=category,
                               item=item,
                               login=loginLabel['logout'])


@app.route('/categories/<string:category_name>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    user = login_session.get('user', None)

    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(id=item_id).one()
    # If you aren't logged in, redirect to login.
    if user is None:
        flash("Sorry, you need to be login to use that.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user = session.merge(user)
        # If posting to delete an object, check the IDs match.
        if user.id != item.user_id:
            flash("You do not have authority to delete {0}.".format(item.name))
            return redirect(url_for('showOneCategoryAndItems',
                                     category_name=category_name))
        # If they match, delete the item.
        session.delete(item)
        session.commit()
        flash("{0} has been deleted from {1}.".format(item.name,
                                                      category.name))
        return redirect(url_for('showOneCategoryAndItems',
                                category_name=category_name))
    else:
        # Else you are using a GET request.
        return render_template('deleteItem.html', category=category,
                               item=item,
                               login=loginLabel['logout'])


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

def googleLogout(token):
    url = 'https://accounts.google.com/o/oauth2/revoke'
    params = { 'token': token }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        return
    else:
        return respondWith("Error processing logout", 500)



if __name__ == '__main__':
    app.secret_key = "password"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
