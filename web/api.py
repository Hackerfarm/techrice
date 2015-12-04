from flask import Flask

flapp = Flask(__name__)

### Restify the app
from flask.ext import restful
rest_api = restful.Api(flapp)

# from flask_limiter import Limiter
# limiter = Limiter(flapp, global_limits=["30 per minute"])


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

dburi = 'postgresql://halfdan@localhost:5432/techrice'

Base = declarative_base()
engine = create_engine('postgresql://halfdan:halfdan@localhost/techrice', convert_unicode = True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
session._model_changes = {}
Base.query = session.query_property()

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Table, Boolean
from sqlalchemy.exc import DataError
from sqlalchemy.orm import object_mapper, class_mapper, relationship, backref
from collections import Iterable


from datetime import datetime, timedelta



class ExtendedBase(object):

	created = sqlalchemy.Column(DateTime, default=datetime.utcnow, nullable=False)
	updated = sqlalchemy.Column(DateTime, default=datetime.utcnow, nullable=False)


	def json(self):
		assert False, "Not implemented"

	@classmethod
	def query_created_interval(cls, start, finish):
		start = datetime.fromtimestamp(start)
		finish = datetime.fromtimestamp(finish)
		return cls.query.filter((cls.created > start) & (cls.created < finish))

	@classmethod
	def query_updated_interval(cls, start, finish):
		start = datetime.fromtimestamp(start)
		finish = datetime.fromtimestamp(finish)
		return cls.query.filter((cls.updated > start) & (cls.updated < finish))

	@classmethod
	def create(cls, *args, **kwargs):
		instance = cls(*args, **kwargs)
		session.add(instance)
		session.commit()
		return instance

	@classmethod
	def first(cls):
		return cls.query.first()

	@classmethod
	def last(cls):
		return cls.query.order_by(cls.id.desc()).first()

	@classmethod
	def all(cls):
		return cls.query.all()

	@classmethod
	def find(cls, id):
		return cls.query.filter_by(id = id).first()

	@classmethod
	def delete(cls, id):
		success = cls.query.filter_by(id = id).delete()
		manager.session.commit()
		return success

	def __repr__(self):
		return str(self.json())


@sqlalchemy.event.listens_for(ExtendedBase, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated = datetime.utcnow()


class Site(ExtendedBase, Base):

	__tablename__ = 'sites'

	id = Column( Integer, primary_key = True)
	alias = Column( String(100) )
	nodes = relationship('Node', cascade='all,delete-orphan', passive_deletes=True, backref = backref('site', single_parent = True))

	def __init__(self, alias = None, nodes = []):
		self.alias = alias
		assert isinstance(nodes, Iterable), 'nodes must be iterable'
		for node in nodes:
			assert isinstance(node, Node), 'Each item in nodes must be an instance of type Node'
			self.nodes.append(node)

	def json(self):
		return {'alias': self.alias, 'id': self.id, 'nodes': map(lambda n: n.id, self.nodes)}


class Node(ExtendedBase, Base):
	
	__tablename__ = 'nodes'
	
	id = Column( Integer, primary_key = True )
	alias = Column( String(100) )
	longitude = Column( Float()) 
	latitude = Column( Float())
	
	nodetype_id = Column( Integer, ForeignKey('nodetypes.id', ondelete = 'SET NULL') )
	site_id = Column( Integer, ForeignKey('sites.id', ondelete = 'SET NULL') )
	sensors = relationship('Sensor', cascade='all,delete-orphan', passive_deletes=True, backref = backref('node'))

	def __init__(self, node_type = None, site = None, alias = None, sensors = [], longitude = None, latitude = None, **kwargs):
		assert isinstance(sensors, Iterable), 'sensors must be iterable'
		for sensor in sensors:
			assert isinstance(sensor, Sensor), 'Each item in sensors must be an instance of type Sensor'
			self.sensors.append(sensor)

		self.longitude = longitude
		self.latitude = latitude
		self.alias = alias
		self.nodetype = node_type

		if site: 
			assert isinstance(site, Site), 'site must be an instance of %s'%type(Site)
			self.site = site


	def json(self):
		return {'alias': self.alias, 'id': self.id, 'longitude': self.longitude, 'latitude': self.latitude, 'site_id': self.site_id, 'sensors': map(lambda s: s.id, self.sensors)}


class NodeType(ExtendedBase, Base):
	__tablename__ = 'nodetypes'
	id = Column(Integer(), primary_key = True)
	name = Column(String(), unique = True)
	nodes = relationship( 'Node', backref = backref('nodetype'))
	# sensortypes = relationship('SensorType', backref = backref('sensors'))

	def __init__(self, name):
		self.name = name

	def json(self):
		return {'id': self.id, 'name': self.name, 'nodes': map(lambda n: n.id, self.nodes)}

# class Unit(ExtendedBase, Base):
# 	__tablename__ = 'units'

# 	id = Column(Integer, primary_key = True)


class SensorType(ExtendedBase, Base):
	__tablename__ = 'sensortypes'

	id = Column( Integer, primary_key = True)
	name = Column( String() )
	unit = Column( String() )
	
	sensors = relationship('Sensor', backref = backref('sensortype'))

	def __init__(self, name, unit, **kwwargs):
		self.name = name
		self.unit = unit

	def json(self):
		return {'id': self.id, 'name': self.name, 'unit': self.unit, 'sensors': map(lambda s: s.id, self.sensors)}


class Sensor(ExtendedBase, Base):
	__tablename__ = 'sensors'
	
	id = Column( Integer, primary_key = True )
	alias = Column( String() )
	# latest_reading = Column( Integer, ForeignKey('readings.id'))
	
	readings = relationship('Reading', cascade='all,delete-orphan', passive_deletes=True, backref = backref('sensor', single_parent = True))

	node_id = Column( Integer, ForeignKey('nodes.id', ondelete = 'CASCADE') )
	sensortype_id = Column( Integer, ForeignKey('sensortypes.id', ondelete = 'SET NULL') )

	def __init__(self, node = None, sensortype = None, alias = None, readings = [], **kwargs):
		self.sensortype = sensortype
		self.node = node
		self.alias = alias
		
	def json(self):
		return {'id': self.id, 'alias': self.alias, 'node_id': self.node_id, 'sensortype_id': self.sensortype_id, 'readings': map(lambda r: r.id, self.readings), 'created': str(self.created), 'updated': str(self.updated)}

	


class Reading(ExtendedBase, Base):
	__tablename__ = 'readings'

	id = Column( Integer, primary_key = True )
	timestamp = Column( DateTime() )
	value = Column( Float() )
	sensor_id = Column( Integer, ForeignKey('sensors.id', ondelete = 'CASCADE') )

	def __init__(self, sensor, value, timestamp):
		self.sensor = sensor
		self.value = value
		if isinstance(timestamp, datetime):
			self.timestamp = timestamp
		else:
			self.timestamp = datetime.fromtimestamp(timestamp)

	def json(self):
		return {'id': self.id, 'sensor_id': self.sensor_id, 'value': self.value, 'timestamp': str(self.timestamp), 'created': str(self.created), 'updated': str(self.updated)}










# from flask_security import RoleMixin, UserMixin
# from flask.ext.sqlalchemy import SQLAlchemy
# from flask_security.datastore import UserDatastore
# from flask_security import Security


# roles_users = Table('roles_users', Base.metadata,
# 	Column('user_id', Integer(), ForeignKey('users.id')),
# 	Column('role_id', Integer(), ForeignKey('roles.id'))
# 	)

# class Role(Base, RoleMixin):
# 	__tablename__ = 'roles'
# 	id = Column(Integer(), primary_key = True)
# 	name = Column(String(100), nullable = False, unique = True)
# 	description = Column(String(255))

# class User(Base, UserMixin):
# 	__tablename__ = 'users'
# 	id = Column(Integer(), primary_key = True)
# 	email = Column(String(255), unique=True)
# 	password = Column(String(255))
# 	active = Column(Boolean())
# 	confirmed_at = Column(DateTime())

# # Setup Flask-Security
# user_datastore = UserDatastore(User, Role)
# security = Security(flapp, user_datastore)

# from flask_security import auth_token_required, http_auth_required
# from flask import jsonify


# # @auth_token_required
# @flapp.route('/authtest/', methods=['GET'])
# @http_auth_required
# def dummyAPI():
#     ret_dict = {
#         "Key1": "Value1",
#         "Key2": "value2"
#     }
#     return jsonify(items=ret_dict)

# @flapp.before_first_request
# def create_user():
#     # create_all()
#     if not User.query.first():
#         user_datastore.create_user(email='test@example.com', password='humle')
#         session.commit()



from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

# Create app
# app = Flask(__name__)
flapp.config['DEBUG'] = True
flapp.config['SECRET_KEY'] = 'super-secret'
flapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

# Create database connection object
db = SQLAlchemy(flapp)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(flapp, user_datastore)

# Create a user to test with
@flapp.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='matt@nobien.net', pasœsword='password')
    db.session.commit()

# Views
@flapp.route('/')
@login_required
def home():
    return render_template('index.html')











#################################################################
#### API resources
#################################################################

from flask import request
import ujson




class SiteResource(restful.Resource):
	def get(self, site_id = None):
		site = Site.query.filter_by(id = site_id).first()
		if site: return site.json()

	def delete(self, site_id = None):
		site = Site.query.filter_by(id = site_id).first()
		if site: 
			Site.delete(site.id)
			return site.json()

	def post(self):
		alias = request.form.get('alias', None)
		site = Site.create(alias = alias)
		return site.json()

rest_api.add_resource(SiteResource, '/site/<int:site_id>', '/site')


class SiteListResource(restful.Resource):
	def get(self):
		sites = Site.query.all()
		return [site.json() for site in sites]
		
rest_api.add_resource(SiteListResource, '/sites')



class NodeResource(restful.Resource):
	
	def get(self, node_id = None):
		node = Node.query.filter_by(id = node_id).first()
		if node: return node.json()

	def delete(self, node_id = None):
		node = Node.query.filter_by(id = node_id).first()
		if node: 
			Node.delete(id = node.id)
			return node.json()
		
	def post(self):
		args = {}
		
		args.update({'alias' : request.form.get('alias', None)})
		args.update({'longitude' : request.form.get('longitude', None)})
		args.update({'latitude' : request.form.get('latitude', None)})

		site_id = request.form.get('site_id', None)
		if site_id: 
			site = Site.query.filter_by(id = site_id).first()
			if site: args.update({'site' : site})
			else: return 'site {} not found'.format(site_id)
		else: return 'missing site_id'

		nodetype_id = request.form.get('nodetype_id', None)
		if nodetype_id: 
			nodetype = NodeType.query.filter_by(id = nodetype_id).first()
			if nodetype: args.update({'nodetype' : nodetype}) 
			else: return 'nodetype {} not found'.format(nodetype_id)
		else: return 'missing nodetype_id'
		
		node = Node.create(**args)
		return node.json()		

rest_api.add_resource(NodeResource, '/node/<int:node_id>', '/node')


class NodeListResource(restful.Resource):
	def get(self):		
		site_id = request.args.get('site_id')
		nodes = Node.query.filter(Node.site_id == site_id).all()
		return [node.json() for node in nodes]

rest_api.add_resource(NodeListResource, '/nodes', '/node/all')




			


class SensorResource(restful.Resource):
	def get(self, sensor_id = None):
		sensor = Sensor.query.filter_by(id = sensor_id).first()
		if sensor:
			return sensor.json()

	def delete(self, sensor_id = None):
		sensor = Sensor.query.filter_by(id = sensor_id).first()
		if sensor:
			Sensor.delete(id = sensor.id)
			return sensor.json()

	def post(self):
		args = {}
		
		node_id = request.form.get('node_id')
		if node_id: 
			node = Node.query.filter_by(id = node_id).first()
			if node: args.update({'node' : node})
			else: return 'node {} not found'.format(node_id)
		else: return 'missing node_id'

		sensortype_id = request.form.get('sensortype_id')
		if sensortype_id: 
			sensortype = SensorType.query.filter_by(id = sensortype_id).first()
			if sensortype: args.update({'sensortype' : sensortype})
			else: return 'sensortype {} not found'.format(sensortype_id)
		else: return 'missing sensortype_id'

		args.update({'alias': request.form.get('alias')})

		Sensor.create(**args)

rest_api.add_resource(SensorResource, '/sensor/<int:sensor_id>')


class SensorListResource(restful.Resource):
	def get(self):
		node_id = request.args.get('node_id')
		sensors = Sensor.query.filter(Sensor.node_id == node_id).all()
		return [sensor.json() for sensor in sensors]

rest_api.add_resource(SensorListResource, '/sensors')


class ReadingResource(restful.Resource):
	def get(self, reading_id = None):
		reading = Reading.query.filter_by(id = reading_id).first()
		if reading:
			return reading.json()

	def delete(self, reading_id = None):
		reading = Reading.query.filter_by(id = reading_id).first()
		if reading:
			reading.delete(id = reading.id)
			return reading.json()

	def post(self):
		sensor_id = request.form.get('sensor_id')
		value = request.form.get('value')
		timestamp = request.form.get('timestamp')
		
		if not value: return 'missing value'
		if not timestamp: return 'missing timestamp'
		if not sensor_id: return 'missing sensor_id'
		else:
			sensor = Sensor.query.filter_by(id = sensor_id).first()
			reading = Reading.create(sensor = sensor, value = value, timestamp = timestamp)
			return reading.json()


rest_api.add_resource(ReadingResource, '/reading/<int:reading_id>', '/reading')

class ReadingListResource(restful.Resource):
	def get(self):
		sensor_id = request.args.get('sensor_id')
		readings = Reading.query.filter(Reading.sensor_id == sensor_id).all()
		return [reading.json() for reading in readings]

rest_api.add_resource(ReadingListResource, '/readings')



from random import random
import time
import itertools
def seed(sensors = 1, days = 7, interval_seconds = 3600):
	site = Site.create(alias = 'seeded_site')
	node = Node.create(alias = 'seeded_node', site = site, latitude = 35.146623 + random(), longitude = 139.9835682 + random())
	sensortype = SensorType.create(name = 'HC SR-04', unit = 'cm')
	for i in range(sensors):
		sensor = Sensor.create(sensortype = sensortype, node = node, alias = 'water distance %s'%i)
		timestamp = datetime.utcnow() - timedelta(days = 7)
		data = loggeobrowngen()
		n_readings = 0
		while timestamp < datetime.utcnow():
			Reading.create(sensor = sensor, value = data.next(), timestamp = timestamp)
			timestamp += timedelta(seconds = interval_seconds)
			n_readings += 1
	return {'site': site, 'node': node}


from multiprocessing import Process
class FakeRealtimeSensor(Process):
	def __init__(self, sensor_id, start_time, wait_interval = 60):
		Process.__init__(self)
		self.daemon = True
		self.wait_interval = wait_interval
		sensor = Sensor.query.filter(Sensor.id == sensor_id).first()
		if sensor: 
			self.sensor = sensor
		else:
			self.sensor = Sensor.create(alias = 'started at %s'%datetime.utcnow().ctime())
			print '*********** Created new sensor'
			print self.sensor

	def run(self):
		for value in loggeobrowngen():
			reading = Reading.create(sensor = self.sensor, value = value, timestamp = datetime.now())
			print reading
			time.sleep(self.wait_interval)






def get_sensor_period_data(sensor_id, start_datetime, end_datetime):
	data = Reading.query.filter((Reading.sensor_id == sensor_id) & (Reading.timestamp > start_datetime) & (Reading.timestamp < end_datetime)).all()
	xdata = map(lambda r: time.mktime(r.timestamp.timetuple()) * 1000, data)
	# ydata = map(lambda r: r.value, data)
	ydata = list(loggeobrowngen(len(xdata)))
	return xdata, ydata

def get_chart_settings():
	settings = {}
	settings.update({'width': request.args.get('width', 850)})
	settings.update({'height': request.args.get('height', 500)})
	settings.update({'color_category': request.args.get('color_category', 'category20b')})
	# settings.update({'color_category': request.args.get('height', 'category20b')})
	# settings.update({'color_category': request.args.get('height', 'category20b')})

	return settings


from nvd3 import lineChart
@flapp.route('/chart/weekly/sensor/<int:sensor_id>')
def sensor_weekly_chart(sensor_id):
	end_datetime = datetime.utcnow()
	start_datetime = end_datetime - timedelta(days = 7)
	sensor = Sensor.query.filter_by(id = sensor_id).first()
	if not sensor: 
		return "sensor {} not found".format(sensor_id)
	
	xdata, ydata = get_sensor_period_data(sensor_id, start_datetime, end_datetime)
	chart = lineChart(name="sensor {} weekly".format(sensor_id), x_is_date=True, x_axis_format="%b %d %a", **get_chart_settings())
	extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
	chart.add_serie(y=ydata, x=xdata, name=sensor.alias, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent

@flapp.route('/chart/daily/sensor/<int:sensor_id>')
def sensor_daily_chart(sensor_id):
	end_datetime = datetime.utcnow()
	start_datetime = end_datetime - timedelta(days = 1)
	sensor = Sensor.query.filter_by(id = sensor_id).first()
	if not sensor: 
		return "sensor {} not found".format(sensor_id)
	
	xdata, ydata = get_sensor_period_data(sensor_id, start_datetime, end_datetime)
	print xdata
	chart = lineChart(name="sensor {} daily".format(sensor_id), x_is_date=False, x_axis_format="AM_PM", **get_chart_settings())
	extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
	chart.add_serie(y=ydata, x=xdata, name=sensor.alias, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent


@flapp.route('/chart/weekly/node/<int:node_id>')
def node_weekly_chart(node_id):
	end_datetime = datetime.utcnow()
	start_datetime = end_datetime - timedelta(days = 7)
	node = Node.query.filter_by(id = node_id).first()
	if not node: return "node {} not found".format(node_id)
	chart_settings = get_chart_settings()
	chart = lineChart(name="node {} weekly".format(node_id), x_is_date=True, x_axis_format="%b %d %a", **chart_settings)
	for sensor in node.sensors:
		xdata, ydata = get_sensor_period_data(sensor.id, start_datetime, end_datetime)
		extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
		chart.add_serie(y=ydata, x=xdata, name=sensor.alias, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent



import itertools
import math
from random import normalvariate
def loggeobrowngen(n = -1, offset = 50):
	p = 1
	dt = 0.5
	mu = 0
	sigma = 1
	for i in itertools.repeat(1, times = n):
		p *= math.exp((mu - sigma * sigma // 2) * dt +sigma * normalvariate(0, dt * dt))
		yield math.log(p) + offset
		


class TestResources:
	url = 'http://localhost:8080/'

	def test_site_get(self):
		pass

	def test_site_delete(self):
		pass

	def test_site_post(self):
		pass

	def test_sitelist_get(self):
		pass
	

	def test_nodetype_get(self):
		pass

	def test_nodetype_delete(self):
		pass

	def test_nodetype_post(self):
		pass

	def test_nodetypelist_get(self):
		pass


	def test_node_get(self):
		pass

	def test_node_delete(self):
		pass

	def test_node_post(self):
		pass

	def test_nodelist_get(self):
		pass


	def test_sensortype_get(self):
		pass

	def test_sensortype_delete(self):
		pass

	def test_sensortype_post(self):
		pass

	def test_sensortypelist_get(self):
		pass


	def test_sensor_get(self):
		pass

	def test_sensor_delete(self):
		pass

	def test_sensor_post(self):
		pass

	def test_sensorlist_get(self):
		pass


	def test_reading_get(self):
		pass

	def test_reading_delete(self):
		pass

	def test_reading_post(self):
		pass

	def test_readinglist_get(self):
		pass





from flask import render_template, Markup

import uuid
class NodeMarker(object):
	def __init__(self, longitude, latitude, icon_url = None, infowindow = None, click_redirect = "http://techrice.jp"):
		assert isinstance(longitude, float), 'longitude must be a float'
		assert isinstance(latitude, float), 'latitude must be a float'
		self.longitude = longitude
		self.latitude = latitude
		
		print infowindow
		print type(infowindow)
		# assert isinstance(infowindow, str), 'infowindow must be a string'
		self.infowindow = Markup(infowindow)
		self.uuid = uuid.uuid4().hex

		assert click_redirect, 'click_redirect must be a url'
		self.click_redirect = click_redirect

	def __repr__(self):
		return str(self.__dict__)


@flapp.route("/map/nodes")
def nodes_map():
	nodes = Node.query.filter((Node.longitude != None) & (Node.latitude != None)).all()
	return make_map(nodes)

@flapp.route("/map/site/<int:site_id>")
def site_map(site_id):
	nodes = Node.query.filter((Node.site_id == site_id) & (Node.longitude != None) & (Node.latitude != None)).all()
	return make_map(nodes)


def make_map(nodes):
	markers = [NodeMarker(
		longitude = node.longitude, 
		latitude = node.latitude, 
		infowindow = node.alias, 
		click_redirect = 'http://localhost:8080/chart/weekly/node/{}'.format(node.id)
		) for node in nodes]
	print Markup(render_template("gmap.html", gmaps_api_key = "AIzaSyC5RK9Zsmy4a_Qr2xMoP_PNypjzv0JIaxE", markers = markers))
	return Markup(render_template("gmap.html", gmaps_api_key = "AIzaSyC5RK9Zsmy4a_Qr2xMoP_PNypjzv0JIaxE", markers = markers))



if __name__ == '__main__':
	Base.metadata.create_all(bind=engine)
	# FakeSensor(1, 1).start()
	flapp.run(port = 8080, debug = True)








