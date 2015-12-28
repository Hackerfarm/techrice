from flask.ext.appbuilder import Model
from flask.ext.appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
from app import db
Model.query = db.session.query_property()

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, event
        
from datetime import datetime

class ExtendedBase(object):

	created = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated = Column(DateTime, default=datetime.utcnow, nullable=False)


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

	# @classmethod
	# def create(cls, *args, **kwargs):
	# 	instance = cls(*args, **kwargs)
	# 	session.add(instance)
	# 	session.commit()
	# 	return instance

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

	# @classmethod
	# def delete(cls, id):
	# 	success = cls.query.filter_by(id = id).delete()
	# 	session.commit()
	# 	return success

	def __repr__(self):
		return str(self.json())


@event.listens_for(ExtendedBase, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated = datetime.utcnow()

from sqlalchemy.orm import object_mapper, class_mapper, relationship, backref
class Site(ExtendedBase, Model):

	__tablename__ = 'sites'
	__resource_type__ = 'site'

	id = Column(Integer, primary_key = True)
	alias = Column(String(100) )
	nodes = relationship('Node', cascade='all,delete-orphan', passive_deletes=True, backref = backref('site', single_parent = True))

	def json(self):
		return {'id': self.id, 
				'alias': self.alias, 
				'nodes': map(lambda n: n.id, self.nodes),
				'type' : Site.__resource_type__,
				'created':float(self.created.strftime("%s.%f")),
				'updated':float(self.updated.strftime("%s.%f"))
				}

from pprint import pprint
class Node(ExtendedBase, Model):
	
	__tablename__ = 'nodes'
	__resource_type__ = 'node'
	id = Column(Integer, primary_key = True )
	alias = Column(String(100))
	longitude = Column(Float()) 
	latitude = Column(Float())
	
	nodetype_id = Column(Integer, ForeignKey('nodetypes.id', ondelete = 'SET NULL') )
	site_id = Column(Integer, ForeignKey('sites.id', ondelete = 'SET NULL') )
	sensors = relationship('Sensor', cascade='all,delete-orphan', passive_deletes=True, backref = backref('node'))

	def json(self):
		return pprint({'alias': self.alias, 
				'id': self.id, 
				'longitude': self.longitude, 
				'latitude': self.latitude, 
				'site_id': self.site_id, 
				'sensors': map(lambda s: s.id, self.sensors),
				'type': Node.__resource_type__,
				'nodetype_id':self.nodetype_id,
				'created':float(self.created.strftime("%s.%f")),
				'updated':float(self.updated.strftime("%s.%f"))
				})

class NodeType(ExtendedBase, Model):
	__tablename__ = 'nodetypes'
	id = Column(Integer(), primary_key = True)
	name = Column(String(), unique = True)
	nodes = relationship( 'Node', backref = backref('nodetype'))

	def json(self):
		return {'id': self.id, 'name': self.name, 'nodes': map(lambda n: n.id, self.nodes)}


class SensorType(ExtendedBase, Model):
	__tablename__ = 'sensortypes'

	id = Column(Integer, primary_key = True)
	name = Column(String())
	unit = Column(String())
	
	sensors = relationship('Sensor', backref = backref('sensortype'))

	def json(self):
		return {'id': self.id, 'name': self.name, 'unit': self.unit, 'sensors': map(lambda s: s.id, self.sensors)}


class Sensor(ExtendedBase, Model):
	__tablename__ = 'sensors'
	
	id = Column(Integer, primary_key = True )
	alias = Column(String())
	readings = relationship('Reading', cascade='all,delete-orphan', passive_deletes=True, backref = backref('sensor', single_parent = True))

	node_id = Column(Integer, ForeignKey('nodes.id', ondelete = 'CASCADE') )
	sensortype_id = Column(Integer, ForeignKey('sensortypes.id', ondelete = 'SET NULL') )
		
	def json(self):
		return {'id': self.id, 'alias': self.alias, 'node_id': self.node_id, 'sensortype_id': self.sensortype_id, 'readings': map(lambda r: r.id, self.readings), 'created': str(self.created), 'updated': str(self.updated)}


class Reading(ExtendedBase, Model):
	__tablename__ = 'readings'

	id = Column(Integer, primary_key = True )
	timestamp = Column(DateTime())
	value = Column(Float())
	sensor_id = Column(Integer, ForeignKey('sensors.id', ondelete = 'CASCADE') )

	def __init__(self, sensor, value, timestamp):
		self.sensor = sensor
		self.value = value
		if isinstance(timestamp, datetime):
			self.timestamp = timestamp
		else:
			self.timestamp = datetime.fromtimestamp(timestamp)

	def json(self):
		return {'id': self.id, 'sensor_id': self.sensor_id, 'value': self.value, 'timestamp': str(self.timestamp), 'created': str(self.created), 'updated': str(self.updated)}
