from flask import Flask, render_template, abort, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)


class Project(db.Model):
    """
    sqlite table with an id, and 4 text fields
    """
    id = db.Column('project_id', db.Integer, primary_key=True)
    short_desc = db.Column(db.String(500))
    project_name = db.Column(db.String(500))
    image_url = db.Column(db.String(200))
    long_desc = db.Column(db.String(2000))

    def __init__(self, project_name, short_desc, long_desc, image_url):
        self.project_name = project_name
        self.short_desc = short_desc
        self.image_url = image_url
        self.long_desc = long_desc


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

# todo protect with password
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
        project = Project(request.form['name'], request.form['short_desc'], request.form['long_desc'], request.form['img_url'])
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects'))

