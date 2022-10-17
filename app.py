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

authenticated = False

# set up the routes

# route for the home page
@app.route('/')
def home():
    # docs = db.exampleapp.find({}).sort("created_at", -1)
    return render_template('index.html')

@app.route('/main/<family_code>')
def main(family_code):
    docs = db.items.find({
        "family_code": family_code,
    })
    return render_template('main.html', family_code = family_code, docs = docs)


@app.route('/signup')
def signup():
    # docs = db.exampleapp.find({}).sort("created_at", -1)
    return render_template('signup.html')


@app.route('/login')
def login():
    # docs = db.exampleapp.find({}).sort("created_at", -1)
    return render_template('login.html')

@app.route('/createFamily', methods=['POST'])
def create_family():
    family_code = request.form['fcode']
    family_passcode = request.form['fpasscode']

    db.exampleapp.insert_one(
        {
            "family_code": family_code,
            "family_passcode": family_passcode,
        },
    )

    return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)

@app.route('/enterFamily', methods=['POST'])
def enter_family():
    family_code = request.form['fcode']
    family_passcode = request.form['fpasscode']

    toGo = db.exampleapp.find(
        {
            "family_code": family_code,
            "family_passcode": family_passcode,
        },
    )

    if toGo:
        return redirect(url_for('main', family_code = family_code))
    else:
        return redirect(url_for('home'))

# route to accept form submission and create a new post
@app.route('/create/<family_code>', methods=['POST'])
def create_post(family_code):

    name = request.form['fname']
    message = request.form['fmessage']

    # create a new document with the data the user entered
    doc = {
        "family_code": family_code,
        "name": name,
        "description": message, 
        "created_at": datetime.datetime.utcnow()
    }
    db.items.insert_one(doc) # insert a new document

    return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)

# route to view the edit form for an existing post
@app.route('/edit/<mongoid>')
def edit(mongoid):
    """
    Route for GET requests to the edit page.
    Displays a form users can fill out to edit an existing record.
    """
    doc = db.items.find_one({"_id": ObjectId(mongoid)})
    return render_template('edit.html', mongoid=mongoid, doc=doc) # render the edit template


# route to accept the form submission to delete an existing post
@app.route('/edit/<mongoid>', methods=['POST'])
def edit_post(mongoid):
    name = request.form['fname']
    message = request.form['fmessage']

    doc = {
        # "_id": ObjectId(mongoid), 
        "name": name, 
        "message": message, 
        "created_at": datetime.datetime.utcnow()
    }

    db.items.update_one(
        {"_id": ObjectId(mongoid)}, # match criteria
        { "$set": doc }
    )

    return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)

# route to delete a specific post
@app.route('/delete/<mongoid>')
def delete(mongoid):
    db.items.delete_one({"_id": ObjectId(mongoid)})
    return redirect(url_for('home')) # tell the web browser to make a request for the / route (the home function)


# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e)


# run the app
if __name__ == "__main__":
    app.run(debug = True)
