import logging
from flask import Flask
"""
 Logging configuration
"""

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_envvar('TECHRICE_SETTINGS')
# 
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from flask.ext import restful
rest_api = restful.Api(app)


from app import models, resources, seed, graphs, maps, views, sec
db.create_all()

print app.config

