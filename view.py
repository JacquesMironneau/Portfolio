from flask import Flask, render_template, abort, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from run import app
from models import db, Project, Project_files


@app.route('/')
def hello(name=None):
    """
    Display the index page (with information about me, profile pic...)
    """
    return render_template('index.html')

   
@app.route('/projects/')
def projects():
    """
    Display every list
    TODO: use the projectList.html to display every projects properly
    """
    result = db.session.query(Project).all()
    return render_template('projectList.html', projectList = result)




@app.route('/project/<id>')
def project(id = None):
    """
    Render the template for a given project (with its ID)
    """
    res = db.session.query(Project).filter(Project.id == id).first()

    print(res)
    if res:
        return render_template('project.html', project = res)
    else:
        abort(404)


@app.route('/about/')
def about():
    return 'The about page'

#TODO protect with password
@app.route('/add/', methods = ['GET', 'POST'])
def add():
    """
    IF the request is get: display the form
    else it means that the form has been submited (see add.html)
    => add the fields in the db and redirect to the project list page
    """
    if request.method == 'GET':
        return render_template('add.html')
    else:
        # Add in db
        project = Project(request.form['name'], request.form['short_desc'], request.form['long_desc'])
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects'))

