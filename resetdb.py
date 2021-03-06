from models import *
import os
"""
Standalone script used to dump the database and the images
"""

db.drop_all()
db.create_all()
res = [r.project_name for r in db.session.query(Project).all()]
db.session.query(Project).delete()
db.session.commit()

print('Project database successfully dumped')

dir = 'static/upload/'

if os.path.exists(dir):
    for file in os.listdir(dir):
        os.remove(os.path.join(dir,file))

    print('Images removed')
else:
    os.makedirs(dir)
    print(dir, " created")
