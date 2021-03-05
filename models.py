#coding : utf-8

from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_migrate import Migrate
"""
Models of the web site:
A Project is composed of 0..n project files
A project file is basically an url related to a project

"""
db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not db.engine.has_table("project"):
    db.create_all()

class Project(db.Model):
    """
    sqlite table with an id, and 4 text fields
    """
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    project_desc = db.Column(db.Text, nullable=False)
    project_url = db.Column(db.String(300), nullable=False)
    project_thumbnail = db.Column(db.String(300), nullable=True) # url of the thumbnail

    def __init__(self, project_name, project_desc, project_url, project_thumbnail):
        self.project_name = project_name
        self.project_desc = project_desc
        self.project_url = project_url
        self.project_thumbnail = project_thumbnail
    
    def __str__(self):
        return f"project_id: {self.id}\n   name: {self.project_name}\n    description: {self.project_desc}\n    project_url: {self.project_url}\n   thumbnail_url: {self.project_thumbnail}"

@app.cli.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()
    

    