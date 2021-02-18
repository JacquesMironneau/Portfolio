from flask import Flask, render_template, abort, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from run import app, ALLOWED_EXTENSIONS
from models import db, Project, Project_files
from werkzeug.utils import secure_filename
import os
"""
View (routing) of the project


"""

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

    if not res:
        abort(404)

    bg_img = [k.file_url for k in res.attached_files if k.is_background]

    tmp = [k for k in res.attached_files if not k.is_background]
    other_images = {f"project_image_{str(k)}": tmp[k].file_url for k in range(len(tmp)) if not tmp[k].is_background}

    return render_template('project.html', 
        project_name = res.project_name,
        short_desc= res.short_desc, 
        long_desc = res.long_desc, 
        background_image = bg_img[0] if bg_img else None,
        **other_images)


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
        if not request.form['name']:
            return redirect(url_for('add'))
        project = Project(request.form['name'], request.form['short_desc'], request.form['long_desc'])
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    """
    upload a file in the FILE_FOLDER (use for images/video mainly)
    """
@app.route('/upload/', methods = ['GET','POST'])
def upload():
    print(request)
    if request.method == 'POST':

        file = request.files['file']
        if file.filename == '':
            # handle no selected file
            return 'no selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project_id = request.form['projects']
            p=Project_files(project_id, filename, True if request.form.getlist('is_background') else False)
            db.session.add(p)
            db.session.commit()
            return redirect(url_for('projects'))
    else:
        result = db.session.query(Project).all()
        return render_template('upload.html', projectList = result)

@app.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='upload/' + filename), code=301)
