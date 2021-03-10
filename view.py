from flask import Flask, render_template, abort, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user
from app import app, ALLOWED_EXTENSIONS
from models import db, Project, User
from werkzeug.utils import secure_filename
import toml
import os
import bcrypt


from gdrive_management import service, getFolder, PF_FOLDER_NAME
from googleapiclient.http import MediaFileUpload
import mimetypes


"""
View (routing) of the project

"""


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    """
    Given *user_id*, return the associated User object

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


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


@app.route('/add/', methods = ['GET', 'POST'])
@login_required
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

            drive_folder_id = getFolder()
            metadata = { 'name':filename }
            media = MediaFileUpload(filename, mimetype=mimetypes.guess_type(filename), resumable=True)
            file = service.files().create(body=metadata, media_body=media, fields='id').execute()
            print(f"added file {file}")


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

@app.route('/delete/',methods=['GET','POST'])
@login_required
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


@app.route('/update/',methods=['GET','POST'])
@login_required

def update():
    """
    We select the project then the page redirect us to /update_projects/<selected-id>/
    """
    if request.method == 'GET':
        return render_template('update.html', projectList = Project.query.all())
    else:
        selected_p = request.form['project-id']
        return redirect(url_for('update_project', id = selected_p))

@app.route('/update_project/<id>',methods = ['GET','POST'])
@login_required
def update_project(id):
    try:
        p = Project.query.get(id)
    except Exception:
        return None

    if request.method == 'GET':
        return render_template('update_project.html', selected_project = p)
    else:
        p.project_name = request.form['project-name']
        p.project_desc = request.form['project-desc']
        p.project_url = request.form['project-url']
        if not request.form['project-thumbnail'] == "":
            p.project_thumbnail = request.form['project-thumbnail']
        db.session.commit()
        return redirect(url_for('projects'))

@app.route('/login', methods = ['GET','POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            usr = User.query.get(request.form['user_id'])
            if bcrypt.checkpw(request.form['user_password'].encode('utf-8'),usr.password):
                login_user(usr)
                flash('Logged in successfully')
                
                next = request.args.get('next')
                return redirect(next or url_for('index'))
        except Exception: # TODO(thomas) find exception to use
            print("Sorry this user don't exist")
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))