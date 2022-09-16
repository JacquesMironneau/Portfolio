from flask import Flask, render_template, abort, redirect, url_for, request, flash, session
import toml
from app import app
import os



"""
View (routing) of the project
"""
