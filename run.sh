#!/bin/sh

if [ -z $VIRTUAL_ENV ]; then
	. venv/bin/activate
	export FLASK_APP=view.py
	export FLASK_ENV=development
fi
flask run
