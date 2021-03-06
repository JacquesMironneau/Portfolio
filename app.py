from flask import Flask
import os
import secrets
import logging

"""
    Application settings and configuration
    we here chose between a remote psql or a local sqlite database according to the env var
"""
app = Flask(__name__)


UPLOAD_FOLDER = 'static/upload/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
basedir = os.path.abspath(os.path.dirname(__file__))

if 'PEF_DB' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['PEF_DB']
else:
    print("Please fill PEF_DB env variable with the db connection string")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = secrets.token_urlsafe(16)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 80))

if __name__ != '__main__':
    #import view
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)