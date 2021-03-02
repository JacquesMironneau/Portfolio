# Portfolio

Highly customisable and easy to update web based Portfolio. The aim of this project is to provide an out of the box portfolio to present project, ideas... in an easy way.The project uses Flask framework, with jinja2 templates for rendering and sqlite3 for the data storage.

<p align="center">
<img src="readme_res/main_page.png" width=500> 
</p>

### Set up and run:
```
python3 -m venv .
. venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=view.py
flask run
```
### Routes:

Main page: (Information about the person)
`/`
To upload images, gif, video to a project:
`/upload/`
To add a project:  
`/add/`  

To display the existing projects  
`/projects/`
Details on a given project
`/project/[n]`
n is here the project id

### TODO:  
- [ ] Docker compose  
- [ ] Style project page
