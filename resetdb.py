from view import *

res = [r.project_name for r in db.session.query(Project).all()]
print(res)
db.session.query(Project).delete()
db.session.commit()

print('Project database successfully dumped')
