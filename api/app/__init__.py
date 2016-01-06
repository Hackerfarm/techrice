import logging
from flask import Flask
# from flask.ext.appbuilder import SQLA, AppBuilder


"""
 Logging configuration
"""

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object('config')

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask.ext import restful
rest_api = restful.Api(app)


from app import models, resources, seed, graphs, maps, views, sec
db.create_all()

