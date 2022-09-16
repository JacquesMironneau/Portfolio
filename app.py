from flask import Flask
import os
import secrets
import logging
from flask import Flask, render_template, abort, redirect, url_for, request, flash, session
import toml
from datetime import date

"""
    Application settings and configuration
    we here chose between a remote psql or a local sqlite database according to the env var
"""
app = Flask(__name__)
UPLOAD_FOLDER = 'static/upload/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
basedir = os.path.abspath(os.path.dirname(__file__))

# if 'PEF_DB' in os.environ:
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['PEF_DB']
# else:
#     print("Please fill PEF_DB env variable with the db connection string")
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
print(upload_folder, "upload_folder")
config = toml.load("config.toml")
user_data = config['data']
projectsList = config['projects']
today = date.today()
born = date(user_data.get('birth_year'), user_data.get('birth_month'), user_data.get('birth_day'))
user_data['age'] =  today.year - born.year - ((today.month, today.day) < (born.month, born.day))
print("data", user_data)
print("projecets", projectsList)


@app.route('/')
def index():
    """
        Display the index page (with information about me, profile pic...)
    """
    print(user_data)
    return render_template('index.html', data=user_data)

@app.route('/projects/')
def projects():
    """
        Display every list
    """
    for k in projectsList:
        print(k)
        # k.update({'img': os.path.join(upload_folder, k.get('image'))})
        # k.update({'image': os.path.join(upload_folder, k.get('image'))})
        print(k)
    return render_template('projectList.html', projectList = projectsList)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 80))

if __name__ != '__main__':
    #import view
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)