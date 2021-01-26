from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)

   
@app.route('/projects/')
def projects():
    return 'The project page'

names = ['salut', 'toma']


@app.route('/project/<projectname>')
def project(projectname = None):

    if projectname in names:
        return render_template('project.html', projectname = projectname)
    else:
        abort(404)


@app.route('/about')
def about():
    return 'The about page'
