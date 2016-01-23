from app import db
from datetime import datetime
from flask.ext.sqlalchemy import event

class ExtendedBase(object):

	created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


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
		db.session.add(instance)
		db.session.commit()
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
		db.session.commit()
		return success

	def __repr__(self):
		return str(self.json())


@event.listens_for(ExtendedBase, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated = datetime.utcnow()


class Site(ExtendedBase, db.Model):

	__tablename__ = 'sites'
	__resource_type__ = 'site'

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100) )
	nodes = db.relationship('Node', cascade='all,delete-orphan', passive_deletes=True, backref = db.backref('site', single_parent = True))

	def json(self):
		return {'id': self.id, 
				'name': self.name, 
				'nodes': map(lambda n: n.id, self.nodes),
				'type' : Site.__resource_type__,
				'created':float(self.created.strftime("%s.%f")),
				'updated':float(self.updated.strftime("%s.%f"))
				}



class Node(ExtendedBase, db.Model):
	
	__tablename__ = 'nodes'
	__resource_type__ = 'node'
	id = db.Column(db.Integer, primary_key = True )
	name = db.Column(db.String(100))
	longitude = db.Column(db.Float()) 
	latitude = db.Column(db.Float())
	
	nodetype_id = db.Column(db.Integer, db.ForeignKey('nodetypes.id', ondelete = 'SET NULL') )
	site_id = db.Column(db.Integer, db.ForeignKey('sites.id', ondelete = 'SET NULL') )
	sensors = db.relationship('Sensor', cascade='all,delete-orphan', passive_deletes=True, backref = db.backref('node'))

	def json(self):
		return {'name': self.name, 
				'id': self.id, 
				'longitude': self.longitude, 
				'latitude': self.latitude, 
				'site_id': self.site_id, 
				'sensors': map(lambda s: s.id, self.sensors),
				'type': Node.__resource_type__,
				'nodetype_id':self.nodetype_id,
				'created':float(self.created.strftime("%s.%f")),
				'updated':float(self.updated.strftime("%s.%f"))
				}



class NodeType(ExtendedBase, db.Model):
	__tablename__ = 'nodetypes'
	id = db.Column(db.Integer(), primary_key = True)
	name = db.Column(db.String(), unique = True)
	nodes = db.relationship( 'Node', backref = db.backref('nodetype'))

	def json(self):
		return {'id': self.id, 'name': self.name, 'nodes': map(lambda n: n.id, self.nodes)}


class SensorType(ExtendedBase, db.Model):
	__tablename__ = 'sensortypes'

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(), unique = True)
	unit = db.Column(db.String())
	
	sensors = db.relationship('Sensor', backref = db.backref('sensortype'))

	def json(self):
		return {'id': self.id, 'name': self.name, 'unit': self.unit, 'sensors': map(lambda s: s.id, self.sensors)}


class Sensor(ExtendedBase, db.Model):
	__tablename__ = 'sensors'
	
	id = db.Column(db.Integer, primary_key = True )
	name = db.Column(db.String())
	readings = db.relationship('Reading', cascade='all,delete-orphan', passive_deletes=True, backref = db.backref('sensor', single_parent = True))

	node_id = db.Column(db.Integer, db.ForeignKey('nodes.id', ondelete = 'CASCADE') )
	sensortype_id = db.Column(db.Integer, db.ForeignKey('sensortypes.id', ondelete = 'SET NULL') )
		
	def json(self):
		return {'id': self.id, 'name': self.name, 'node_id': self.node_id, 'sensortype_id': self.sensortype_id, 'readings': map(lambda r: r.id, self.readings), 'created': str(self.created), 'updated': str(self.updated)}


class Reading(ExtendedBase, db.Model):
	__tablename__ = 'readings'

	id = db.Column(db.Integer, primary_key = True )
	timestamp = db.Column(db.DateTime())
	value = db.Column(db.Float())
	sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id', ondelete = 'CASCADE') )

	def __init__(self, sensor, value, timestamp):
		self.sensor = sensor
		self.value = value
		if isinstance(timestamp, datetime):
			self.timestamp = timestamp
		else:
			self.timestamp = datetime.fromtimestamp(timestamp)

	def json(self):
		return {'id': self.id, 'sensor_id': self.sensor_id, 'value': self.value, 'timestamp': str(self.timestamp), 'created': str(self.created), 'updated': str(self.updated)}









