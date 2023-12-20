# all imports
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
from markupsafe import escape
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
import os
import subprocess

# initiate the app
app = Flask(__name__)

# load credentials and configuration options from .env file
import credentials
config = credentials.get()

# debugging on if in dev mode
if config['FLASK_ENV'] == 'development':
    app.debug = True

# connection to i6 database (temporary)
connection = pymongo.MongoClient(config['MONGO_HOST'], 27017, 
                                username=config['MONGO_USER'],
                                password=config['MONGO_PASSWORD'],
                                authSource=config['MONGO_DBNAME'])
db = connection[config['MONGO_DBNAME']]

# set up routess
@app.route('/')
def home():
    # done
    return render_template('index.html')

@app.route('/read')
def read():
    # done
    docs = db.running.find({}).sort("created_at", -1)
    return render_template('read.html', docs=docs)

@app.route('/create')
def create():
    #done
    return render_template('create.html') 

@app.route('/create', methods=['POST'])
def create_post():
    #done
    name = request.form['name']
    thought = request.form['thought']
    first_run = request.form['first_run']

    doc = {
        "name": name,
        "thought": thought, 
        "first_run": first_run,
        "created_at": datetime.utcnow()
    }

    db.running.insert_one(doc) 
    return redirect(url_for('read'))

@app.route('/edit/<mongoid>')
def edit(mongoid):
    doc = db.running.find_one({"_id": ObjectId(mongoid)})
    return render_template('edit.html', mongoid=mongoid, doc=doc) # render the edit template

@app.route('/edit/<mongoid>', methods=['POST'])
def edit_post(mongoid):
    name = request.form['name']
    first_run = request.form['first_run']
    thought = request.form['thought']

    doc = {
        # "_id": ObjectId(mongoid), 
        "name": name, 
        "thought": thought, 
        "first_run": first_run,
        "created_at": datetime.utcnow()
    }

    db.running.update_one(
        {"_id": ObjectId(mongoid)}, 
        { "$set": doc }
    )
    return redirect(url_for('read')) 

@app.route('/delete/<mongoid>')
def delete(mongoid):
    #done
    db.running.delete_one({"_id": ObjectId(mongoid)})
    return redirect(url_for('read')) 

@app.route('/webhook', methods=['POST'])
def webhook():
    # run a git pull command
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    pull_output = process.communicate()[0]
    # pull_output = str(pull_output).strip() # remove whitespace
    process = subprocess.Popen(["chmod", "a+x", "flask.cgi"], stdout=subprocess.PIPE)
    chmod_output = process.communicate()[0]
    # send a success response
    response = make_response('output: {}'.format(pull_output), 200)
    response.mimetype = "text/plain"
    return response

@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e) # render the edit template

if __name__ == "__main__":
    app.run(debug = True)