from flask import Flask, request, session, g, redirect, url_for, abort, \
             render_template, flash
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py


@app.route('/')
def show_entries():
    #entries = cur.fetchall()
    entries = "hello cruel world"
    print('hello')
    return render_template('show_entries.html', entries=entries)

