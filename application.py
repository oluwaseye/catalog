# -------------------
# IMPORTS
# -------------------
from flask import Flask, render_template, request, make_response
from flask import url_for, redirect, flash, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests

# ----------------------
# Database Setup
# ----------------------
engine = create_engine('sqlite:///itemcatalog.db', connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# --------------------------
# Application Flask Instance
# --------------------------
app = Flask(__name__)

# -----------------------------
# Google Signin  Client Secrets
# -----------------------------
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# ----------
# User Login 
# ----------

@app.route('/login')
def showLogin():
    categories = session.query(Category).all()
    # State token to prevent forgery
    login_state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = login_state
    return render_template('login.html', categories=categories, STATE=login_state)

# ----------------
# ** Google Signin  
# ----------------

@app.route('/google_signin', methods=['POST'])
def google_signin():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store  authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        google_oauth = flow_from_clientsecrets('client_secrets.json', scope='')
        google_oauth.redirect_uri = 'postmessage'
        credentials = google_oauth.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    htp = httplib2.Http()
    access_result = json.loads(htp.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if access_result.get('error') is not None:
        response = make_response(json.dumps(access_result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if access_result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if access_result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"'
    "border-radius: 150px;-webkit-border-radius: 150px;"
    "-moz-border-radius: 150px;\"> "
    flash("You are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect a User from login session on google_signin
@app.route('/google_signout')
def google_signout():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = redirect(url_for('showCategories'))
        flash("Current User is Not Connected!!")
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = redirect(url_for('showCategories'))
        flash("You're now logged out!!")
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# ---------------------------
# JSON for catalog items
# ---------------------------

# JSON route for all categories in catalog
@app.route('/categories/json')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


# JSON route for items in a specific category
@app.route('/categories/<path:category_name>/items/json')
def showItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


# JSON route all items in catalog
@app.route('/categories/items/json')
def allItemsJSON():
    items = session.query(Items).order_by(Items.id.asc())
    return jsonify(Items=[i.serialize for i in items])


# JSON route for a specific item info
@app.route('/categories/<path:category_name>/<path:item_name>/json')
def itemInfoJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(name=item_name,
                                          category=category).one()
    return jsonify(item=[item.serialize])


# --------------------------
# CRUD for categories
# --------------------------

# Show all categories
@app.route('/')
@app.route('/categories/', methods=['GET'])
def showCategories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publicCategories.html', categories=categories)
    else:
        return render_template('privateCategories.html', categories=categories)


# Create a new Category
@app.route('/categories/new', methods=['GET', 'POST'])
def newCategory():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        addCategory = Category(name=request.form['name'],
                               picture=request.form['picture'],
                               user_id=login_session['user_id'])
        session.add(addCategory)
        session.commit()
        flash('New Category Created!!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html', categories=categories)


# Edit a Category
@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
            "alert('You are not authorized to edit this Category." \
            " Please create your own Category in order to edit.');" \
               "}</script><body onload='myFunction()''> "
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        if request.form['picture']:
            editedCategory.picture = request.form['picture']
        session.add(editedCategory)
        session.commit()
        flash('Category %s edited successfully!!' % editedCategory.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html',
                               category=editedCategory, categories=categories)


# Delete a Category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    deletedCategory = session.query(Category).filter_by(id=category_id).one()
    if deletedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
            "alert('You are not authorized to delete this Category." \
            " Please create your own Category in order to delete.');" \
            "}</script><body onload='myFunction()''> "
    if request.method == 'POST':
        session.delete(deletedCategory)
        session.commit()
        flash('Category Deleted !!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',
                               category=deletedCategory, categories=categories)


# -------------------------
# CRUD for catalog items
# -------------------------

# Show Category Items
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    items = session.query(Items).filter_by(category_id=category_id).all()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session:
        return render_template('publicItems.html', items=items,
                               categories=categories, category=category,
                               creator=creator)
    else:
        return render_template('privateItems.html', items=items,
                               categories=categories, category=category,
                               creator=creator)


# Display an item's info in the category
@app.route('/categories/<path:category_name>/<path:item_name>/')
def showItemInfo(category_name, item_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(name=item_name).one()
    return render_template('showItemInfo.html', item=item,
                           category=category, categories=categories)


# Create new item in a category
@app.route('/categories/<path:category_name>/item/new',
           methods=['GET', 'POST'])
def createNewItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {" \
            "alert('You are not authorized to add items to this category." \
            " Please create your own category in order to add items.');" \
               "}</script><body onload='myFunction()''> "
    if request.method == 'POST':
        addItem = Items(
            name=request.form['name'],
            image=request.form['image'],
            price=request.form['price'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            category=session.query(Category).filter_by(
                name=category_name).one()
        )
        session.add(addItem)
        session.commit()
        flash('New Item Added !!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newItem.html',
                               categories=categories, category=category)


# Edit an item in a category
@app.route('/categories/<int:category_id>/item/<path:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    editedItem = session.query(Items).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {" \
            "alert('You are not authorized to edit items to this Category." \
            " Please create your own Category in order to edit items.');" \
            "}</script><body onload='myFunction()''> "
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['image']:
            editedItem.image = request.form['image']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category = session.query(Category).filter_by(
                name=request.form['category']).one()
        session.add(editedItem)
        session.commit()
        flash('Item Edited Successfully !!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editItem.html', categories=categories,
                               category=category, item=editedItem)


# Delete an item in a category
@app.route('/categories/<int:category_id>/item/<path:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    deletedItem = session.query(Items).filter_by(name=item_name).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {" \
            "alert('You are not authorized to delete " \
            "menu items in this Category." \
            "Please create your own Category in order to delete items.');" \
            "}</script><body onload='myFunction()''> "
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Item deleted !!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteItem.html',
                               item=deletedItem, category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
