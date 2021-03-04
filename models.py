#coding : utf-8

from flask_sqlalchemy import SQLAlchemy
from app import app
"""
Models of the web site:
A Project is composed of 0..n project files
A project file is basically an url related to a project

"""
db = SQLAlchemy(app)


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
        
# class Project_files(db.Model):
#     """
#     sqlite table that represents files attached to a project
#     project_id integer foreign key (this one references as projects(project_id))
#     file_url string(100)
#     """
#     id = db.Column(db.Integer, primary_key=True)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
#     file_url = db.Column(db.String(100))
#     is_background = db.Column(db.Boolean)


#     def __init__(self, project_id, file_url, is_background):
#         self.project_id = project_id
#         self.file_url = file_url
#         self.is_background = is_background

#     def __str__(self):
#         return f"    file_id = {self.id}\n    idproject = {self.project_id}\n    url :{self.file_url} \n isbackground {self.is_background}\n"


# def init_db():
#     db.drop_all()
#     db.create_all()

#     file1 = Project_files(1,"/url/url/toma", False) 
#     file2 = Project_files(1,"/url/aurl/toma", True) 
#     file3 = Project_files(1,"/url/burl/toma", False) 
    
#     project = Project('Projetnom', 'description pitite', 'long')
#     db.session.add(project)
#     db.session.add(file1)
#     db.session.add(file2)
#     db.session.add(file3)
#     db.session.commit()