"""pythonanywhere wsgi uses this file to import flask app"""
from flaskr import create_app

app = create_app()
