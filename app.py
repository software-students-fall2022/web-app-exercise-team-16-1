#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values

import pymongo
import datetime
from bson.objectid import ObjectId
import sys

# instantiate the app
app = Flask(__name__)

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
config = dotenv_values(".env")

# connect to the database
cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
try:
    # verify the connection works by pinging the database
    cxn.admin.command('ping') # The ping command is cheap and does not require auth.
    db = cxn[config['MONGO_DBNAME']] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    # render_template('error.html', error=e) # render the edit template
    print(' *', "Failed to connect to MongoDB at", config['MONGO_URI'])
    print('Database connection error:', e) # debug

# set up the routes
@app.route('/')
def home():
    docs = db.families.find({})
    itemsList = db.items.find({})
    usersList = db.users.find({})
    return render_template('index.html', docs=docs, itemsList = itemsList, usersList = usersList)

@app.route('/main/<family_code>')
def main(family_code):
    docs = db.items.find({
        "family_code": family_code,
    }).sort("created_at", -1)
    return render_template('main.html', family_code = family_code, docs = docs)


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/createFamily', methods=['POST'])
def create_family():
    family_code = request.form['fcode']
    family_passcode = request.form['fpasscode']
    username = request.form['fusername']

    db.families.insert_one(
        {
            "family_code": family_code,
            "family_passcode": family_passcode,
        },
    )

    db.users.insert_one(
        {
            "family_code": family_code,
            "username": username,
        },
    )
    
    # tell the browser to make a request for the / route (the home function)
    return redirect(url_for('home')) 

@app.route('/family/<family_code>')
def family(family_code):
    docs = db.users.find({
        "family_code": family_code,
    })
    return render_template('family.html', family_code = family_code, usersList = docs)

@app.route('/enterFamily', methods=['POST'])
def enter_family():
    family_code = request.form['fcode']
    family_passcode = request.form['fpasscode']
    username = request.form['fusername']

    toGo = db.families.count_documents(
        {
            "family_code": family_code,
            "family_passcode": family_passcode,
        },
    ) > 0


    # tell the browser to make a request for correct route
    if toGo:
        user = {
            "family_code": family_code,
            "username": username,
        }
        # insert a new document
        db.users.insert_one(user) 
        return redirect(url_for('main', family_code = family_code))
    else:
        return redirect(url_for('home'))

@app.route('/create/<family_code>')
def create(family_code):
    return render_template('add.html', family_code = family_code)

@app.route('/create/<family_code>', methods=['POST'])
def create_item(family_code):

    name = request.form['fname']
    quantity = request.form['fquantity']
    deadline = request.form['fdeadline']
    urgency = request.form['furgent']
    location = request.form['flocation']

    # create a new document with the data the user entered
    doc = {
        "family_code": family_code,
        "name": name,
        "quantity": quantity,
        "deadline": deadline,
        "urgency": urgency,
        "location": location, 
        "created_at": datetime.datetime.utcnow()
    }
    # insert a new document
    db.items.insert_one(doc) 
    
    # tell the browser to make a request for the main route
    return redirect(url_for('main', family_code = family_code)) 

@app.route('/edit/<mongoid>')
def edit(mongoid):
    family_code  = request.args.get('family_code', None)
    doc = db.items.find_one({"_id": ObjectId(mongoid)})
    return render_template('edit.html', mongoid=mongoid, doc=doc, family_code = family_code) # render the edit template


@app.route('/edit/<mongoid>', methods=['POST'])
def edit_item(mongoid):
    name = request.form['fname']
    family_code  = request.args.get('family_code', None)
    deadline = request.form['fdeadline']
    quantity = request.form['fquantity']
    urgency = request.form['furgent']
    location = request.form['flocation']

    doc = {
        "family_code": family_code,
        "name": name,
        "quantity": quantity,
        "deadline": deadline,
        "urgency": urgency,
        "location": location, 
        "created_at": datetime.datetime.utcnow()
    }

    db.items.update_one(
        {"_id": ObjectId(mongoid)},
        { "$set": doc }
    )
    
    # tell the browser to make a request for the main route
    return redirect(url_for('main', family_code = family_code)) 

@app.route('/delete/<mongoid>')
def delete(mongoid):
    family_code  = request.args.get('family_code', None)
    db.items.delete_one({"_id": ObjectId(mongoid)})

    # tell the web browser to make a request for the main route
    return redirect(url_for('main', family_code = family_code)) 

@app.route('/main/<family_code>', methods=['POST'])
def search(family_code):
    search = request.form['search']
    docs = db.items.find({
        "family_code": family_code,
        "name": { "$regex": search, "$options": "i" }
    }).sort("created_at", -1)
    return render_template('main.html', family_code = family_code, docs = docs)


# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e)


# run the app
if __name__ == "__main__":
    app.run(debug = True)
