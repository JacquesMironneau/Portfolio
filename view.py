from flask import Flask, render_template, abort, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from app import app, ALLOWED_EXTENSIONS
from models import db, Project
from werkzeug.utils import secure_filename
import toml
import os
"""
View (routing) of the project


"""
user_data = toml.load("config.toml")

@app.route('/')
def index():
    """
    Display the index page (with information about me, profile pic...)
    """
    return render_template('index.html', **user_data)

@app.route('/projects/')
def projects():
    """
    Display every list
    TODO: use the orojectList.html to display every projects properly
    """
    result = db.session.query(Project).all()
    return render_template('projectList.html', projectList = result)


#TODO protect with password
@app.route('/add/', methods = ['GET', 'POST'])
def add():
    """
    IF the request is get: display the form
    else it means that the form has been submited (see add.html)
    => add the fields in the db and redirect to the project list page
    """
    if request.method == 'GET':
        return render_template('add.html', projectList = db.session.query(Project).all())
    else:
        # Add in db
        if not request.form['project_name']:
            return redirect(url_for('add'))

        file = request.files['project_thumbnail']
        if file.filename == '':
            # handle no selected file
            return 'no selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.abspath(__file__),app.config['UPLOAD_FOLDER'], filename))

        project = Project(request.form['project_name'], request.form['project_desc'], request.form['project_url'], filename)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='upload/' + filename), code=301)

@app.route('/delete',methods=['GET','POST'])
def delete():
    """
    Request is form
    so we redirect to a page like /delete/id where id is selected from the delete_project
    """
    if request.method == 'GET':
        return render_template('delete.html', projectList = db.session.query(Project).all() )
    else:
        id = request.form['delete-project']
        db.session.query(Project).filter(Project.id == id).delete()
        db.session.commit()
        return redirect(url_for('delete'))