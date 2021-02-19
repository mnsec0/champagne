from flask import Flask, render_template, request, redirect, url_for
from flaskext.markdown import Markdown
import pickle
from os import path as os_path, mkdir as os_mkdir, remove as os_remove
from datetime import datetime
import sys, getopt
import boto3
import pprint
from botocore.config import Config

app = Flask("Champagne")
Markdown(app)

dynamodb = boto3.client('dynamodb', config=Config(region_name='us-east-1'))
pp = pprint.PrettyPrinter(indent=4)






@app.route("/")
def home():
    response = dynamodb.scan(TableName='notes_app')
    response = response['Items']
    return render_template("home.html", notes=response)

@app.route("/addNote")
def addNote():
    return render_template("noteForm.html", headerLabel="New Note", submitAction="createNote", cancelUrl=url_for('home'))

@app.route("/createNote", methods=["post"])
def createNote():
    response = dynamodb.scan(TableName='notes_app')
    response = response['Items']
    if len(response):
        idList = [ int(i['noteid']['N']) for i in response ]
        noteId = str(max(idList)+1)
    else:
        noteId = "1"

    noteTitle = request.form['noteTitle']
    noteMessage = request.form['noteMessage']

    lastModifiedDate = datetime.now()
    lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")
    dynamodb.put_item(TableName='notes_app', Item={'noteid': {'N' : noteId}, 'title': {'S' : noteTitle}, 'lastModifiedDate': {'S': lastModifiedDate}, 'message': {'S' : noteMessage}})

    return redirect(url_for('viewNote', noteId=noteId))

@app.route("/viewNote/<int:noteId>")
def viewNote(noteId):
    noteId = str(noteId)
    note = dynamodb.get_item(TableName='notes_app', Key={'noteid': {'N' : noteId}})
    note = note['Item']

    return render_template("viewNote.html", note=note, submitAction="/saveNote")

@app.route("/editNote/<int:noteId>")
def editNote(noteId):
    noteId = str(noteId)
    note = dynamodb.get_item(TableName='notes_app', Key={'noteid': {'N' : noteId}})
    note = note['Item']
    cancelUrl = url_for('viewNote', noteId=noteId)
    return render_template("noteForm.html", headerLabel="Edit Note", note=note, submitAction="/saveNote", cancelUrl=cancelUrl)

@app.route("/saveNote", methods=["post"])
def saveNote():
    lastModifiedDate = datetime.now()
    lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")




    noteId = str(int(request.form['noteId']))
    noteTitle = request.form['noteTitle']
    noteMessage = request.form['noteMessage']

    dynamodb.put_item(TableName='notes_app', Item={'noteid': {'N' : noteId}, 'title': {'S' : noteTitle}, 'lastModifiedDate': {'S': lastModifiedDate}, 'message': {'S' : noteMessage}})
    return redirect(url_for('viewNote', noteId=noteId))

@app.route("/deleteNote/<int:noteId>")
def deleteNote(noteId):
    dynamodb.delete_item(TableName='notes_app', Key={'noteid' : {'N' : str(noteId)}})






    return redirect("/")

if __name__ == "__main__":
    debug = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:", ["debug"])
    except getopt.GetoptError:
        print('usage: main.py [-h 0.0.0.0] [-p 5000] [--debug]')
        sys.exit(2)

    port = "5000"
    host = "0.0.0.0"
    print(opts)
    for opt, arg in opts:
        if opt == '-p':
            port = arg
        elif opt == '-h':
            host = arg
        elif opt == "--debug":
            debug = True

    app.run(host=host, port=port, debug=debug)

