#coding : utf-8

from flask_sqlalchemy import SQLAlchemy
from app import app
import bcrypt
import click


"""
    Models of the portfolio (tables of the database using the SQLAlchemy ORM)
    A Project is the main unit of the application
    An a user here represent an "administrator" that can perform task to add/delete/update the project
"""

db = SQLAlchemy(app)

if not db.engine.has_table("project"):
    db.create_all()


class Project(db.Model):
    """
        Project unit (here the owner add his realizations (called projects))

        Attributes
        ----------
        A project is composed of an id (system handled), a name, a description
        an url (mainly used to point to the repository for programming project)
        and a thumbnail.
    """
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    project_desc = db.Column(db.Text, nullable=False)
    project_url = db.Column(db.String(300), nullable=False)
    # here a project thumbnail is just the path to the ressource
    project_thumbnail = db.Column(db.String(300), nullable=True) 

    def __init__(self, project_name: str, project_desc: str, project_url: str, project_thumbnail: str):
        self.project_name = project_name
        self.project_desc = project_desc
        self.project_url = project_url
        self.project_thumbnail = project_thumbnail
    
    def __str__(self):
        return f"project_id: {self.id}\n   name: {self.project_name}\n    description: {self.project_desc}\n    project_url: {self.project_url}\n   thumbnail_url: {self.project_thumbnail}"


class User(db.Model):
    """
        An admin user capable of going on admin page and add/delete/update projects

        Attributes
        ------------
        name: str
            the name/login of the user

        password: str
            encrypted password of the user
    """

    __tablename__="pfuser"
    name = db.Column(db.String, primary_key=True)
    password = db.Column(db.LargeBinary)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, name: str, password: str):
        self.name = name
        self.password = password

    def is_active(self):
        """True, as all users are active"""
        return True
    
    def get_id(self):
        """Return email to satisfy Flask-Login's requirements"""
        return self.name
    
    def is_authenticated(self):
        """Return true if the user is authenticated"""
        return self.authenticated

    def is_anonymous(self):
        """False"""
        return False

"""
 App CLI command - WIP
 TODO: enable their functionment in any environment
"""
@app.cli.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()

@app.cli.command("add-user")
@click.argument("login")
@click.argument("password")
def add_user(login, password):
    user = User(login, password)
    db.session.add(user)
    db.session.commit()
    print(f"User added: {login} ")
