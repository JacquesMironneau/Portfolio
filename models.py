from flask_sqlalchemy import SQLAlchemy
from run import app

db = SQLAlchemy(app)


class Project(db.Model):
    """
    sqlite table with an id, and 4 text fields
    """
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    long_desc = db.Column(db.Text)
    #TODO: le delete cascade ne marche pas
    attached_files = db.relationship('Project_files', cascade = "all,delete")

    def __init__(self, project_name, short_desc, long_desc):
        self.project_name = project_name
        self.short_desc = short_desc
        self.long_desc = long_desc
    
    def __str__(self):
        return f"   project_id: {self.id}\n    name: {self.project_name}\n    short description: {self.short_desc}\n    osef: {self.long_desc}"
        
class Project_files(db.Model):
    """
    sqlite table that represents files attached to a project
    project_id integer foreign key (this one references as projects(project_id))
    file_url string(100)
    """
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    file_url = db.Column(db.String(100))


    def __init__(self, project_id, file_url):
        self.project_id = project_id
        self.file_url = file_url

    def __str__(self):
        return f"    file_id = {self.id}\n    idproject = {self.project_id}\n    url :{self.file_url} \n"


def init_db():
    db.drop_all()
    db.create_all()

    file1 = Project_files(1,"/url/url/toma") 
    file2 = Project_files(1,"/url/aurl/toma") 
    file3 = Project_files(1,"/url/burl/toma") 
    
    project = Project('Projetnom', 'description pitite', 'long')
    db.session.add(project)
    db.session.add(file1)
    db.session.add(file2)
    db.session.add(file3)
    db.session.commit()