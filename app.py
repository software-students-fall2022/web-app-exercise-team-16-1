from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values
import pymongo

app = Flask(__name__)

config = dotenv_values(".env")

cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)

# route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e)


# run the app
if __name__ == "__main__":
    app.run(debug = True)