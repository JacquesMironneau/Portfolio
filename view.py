from flask import Flask, render_template, abort, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user
from app import app, ALLOWED_EXTENSIONS
from models import db, Project, User
from werkzeug.utils import secure_filename
import toml
import os
import bcrypt

from gdrive_management import *

"""
View (routing) of the project
"""
download_projects_images(app.config['UPLOAD_FOLDER'])

upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])


login_manager = LoginManager()
login_manager.init_app(app)
user_data = toml.load("config.toml")



@login_manager.user_loader
def user_loader(user_id):
    """
        Given *user_id*, return the associated User object

        :param unicode user_id: user_id (name) user to retrieve
    """
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    session['next_url'] = request.url
    print(session.get('next_url'))
    return redirect(url_for('login'))


@app.route('/login', methods = ['GET','POST'])
def login():
    """
        Display a basic login form in order to log in a user
    """
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            usr = User.query.get(request.form['user_id'])
            if bcrypt.checkpw(request.form['user_password'].encode('utf-8'),usr.password):
                login_user(usr, remember=True)
                flash('Logged in successfully')
                
                return redirect(session['next_url'])
        except Exception as e:
            print("Sorry this user don't exist")
            print(e)
            return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
        Logout the actual authenticated/logged user
    """
    logout_user()
    return redirect(url_for('index'))



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
    """
    result = db.session.query(Project).all()
    return render_template('projectList.html', projectList = result)


@app.route('/add/', methods = ['GET', 'POST'])
@login_required
def add():
    ### IF the request is get: display the form
    ### else it means that the form has been submited (see add.html)
    ### => add the fields in the db and redirect to the project list page
    """
        Display the form to add a project
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
        # if the file extension is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
           
            uploadImageToServer(file, filename)

            uploadImageToDriveFolder(filename)


            # finally we create a new project with the informations given by the user and we adding it to the database
            project = Project(request.form['project_name'], request.form['project_desc'], request.form['project_url'], filename)
            db.session.add(project)
            db.session.commit()
            return redirect(url_for('projects'))


def uploadImageToServer(file, filename):
    """
        Upload a given image to the server

        :param bytes file : the binary file we will save on the server
        :param str filename: the name of the file we want to save on the server
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file.save(os.path.join(upload_folder, filename))


def allowed_file(filename:str):
    """
        Checks if the extension of a given is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='upload/' + filename), code=301)

@app.route('/delete/',methods=['GET','POST'])
@login_required
def delete():
    ### Request is form
    ### so we redirect to a page like /delete/id where id is selected from the delete_project
    """
        Display a list of the projects, if one is selected it will be deleted from the database
    """
    if request.method == 'GET':
        return render_template('delete.html', projectList = db.session.query(Project).all() )
    else:
        id = request.form['delete-project']
        image_name = Project.query.get(id).project_thumbnail

        for img in getImages():
            if img.get('name') == image_name:
                gdrive_api.files().delete(fileId=img.get('id')).execute()
                print(f"Deleted file : {image_name} from google drive")
        os.remove(os.path.join(upload_folder, image_name))

        db.session.query(Project).filter(Project.id == id).delete()
        db.session.commit()
        return redirect(url_for('delete'))


@app.route('/update/',methods=['GET','POST'])
@login_required

def update():
    """
        We select the project we want to update/change in a list
    """
    if request.method == 'GET':
        return render_template('update.html', projectList = Project.query.all())
    else:
        selected_p = request.form['project-id']
        return redirect(url_for('update_project', id = selected_p))

@app.route('/update_project/<id>',methods = ['GET','POST'])
@login_required
def update_project(id):
    """
        Display the form to modify/change/update a project's informations
    """
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
            
        if not request.files['project-thumbnail'].filename == '':
            imgs = getImages()
            for img in imgs:
                if img.get('name') == p.project_thumbnail:
                    gdrive_api.files().delete(fileId=img.get('id')).execute()
            # update thumbnail of the project (delete the old one first and set the new path in the project_thumbnail variable)
            os.remove(os.path.join(upload_folder, p.project_thumbnail))
            p.project_thumbnail = request.files['project-thumbnail'].filename

            # update the file in the update folder
            file = request.files['project-thumbnail']
            # if the file extension is allowed
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
            
                uploadImageToServer(file, filename)

                uploadImageToDriveFolder(filename)

        db.session.commit()
        return redirect(url_for('projects'))