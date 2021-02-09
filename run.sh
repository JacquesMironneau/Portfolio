#!/bin/sh

if [ -z $VIRTUAL_ENV ]; then
	. venv/bin/activate
fi
export FLASK_APP=view.py
export FLASK_ENV=development
flask run
