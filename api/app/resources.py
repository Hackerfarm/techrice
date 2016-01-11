from app import rest_api

from flask import request, jsonify
import ujson
from flask.ext import restful

from models import Site, Node, NodeType, Sensor, SensorType, Reading

import sqlalchemy
from datetime import datetime

from flask.ext.security import login_required, http_auth_required



class ApiError(dict):
	def __init__(self, message):
		self['error'] = message	

class ApiObjects(dict):
	def __init__(self, objects = None):
		self['objects'] = objects



class SiteResource(restful.Resource):
	def get(self, site_id = None):
		site = Site.query.filter_by(id = site_id).first()
		if site: 
			return jsonify(ApiObjects(site.json()))
		else: 
			return jsonify(ApiObjects())

	@http_auth_required
	def delete(self, site_id = None):
		site = Site.query.filter_by(id = site_id).first()
		if site: 
			Site.delete(site.id)
			return jsonify(ApiObjects(site.json()))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def post(self):
		name = request.form.get('name', None)
		site = Site.create(name = name)
		if site:
			return jsonify(ApiObjects(site.json()))
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(SiteResource, '/site/<int:site_id>', '/site')


class SiteListResource(restful.Resource):
	def get(self):
		sites = Site.query.all()
		if sites: 
			return jsonify(ApiObjects([site.json() for site in sites]))
		else:
			return jsonify(ApiObjects())
		
rest_api.add_resource(SiteListResource, '/sites')



class NodeResource(restful.Resource):
	
	def get(self, node_id = None):
		node = Node.query.filter_by(id = node_id).first()
		if node: 
			return jsonify(ApiObjects(node.json()))
		else:
			jsonify(ApiObjects())

	@http_auth_required
	def delete(self, node_id = None):
		node = Node.query.filter_by(id = node_id).first()
		if node: 
			Node.delete(id = node.id)
			return jsonify(ApiObjects(node.json()))
		else:
			jsonify(ApiObjects())
	
	@http_auth_required
	def post(self):
		args = {}
		
		args.update({'name' : request.form.get('name', None)})
		args.update({'longitude' : request.form.get('longitude', None)})
		args.update({'latitude' : request.form.get('latitude', None)})

		site_id = request.form.get('site_id', None)
		if site_id: 
			site = Site.query.filter_by(id = site_id).first()
			if site: 
				args.update({'site' : site})
			else: 
				return jsonify(ApiError('site {} not found'.format(site_id)))
		else: 
			return jsonify(ApiError('missing query arg: site_id'))

		nodetype_id = request.form.get('nodetype_id', None)
		if nodetype_id: 
			nodetype = NodeType.query.filter_by(id = nodetype_id).first()
			if nodetype: 
				args.update({'nodetype' : nodetype}) 
			else: 
				return jsonify(ApiError('nodetype {} not found'.format(nodetype_id)))
		
		node = Node.create(**args)
		if node:
			return jsonify(ApiObjects(node.json()))
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(NodeResource, '/node/<int:node_id>', '/node')


class NodeListResource(restful.Resource):
	def get(self):		
		site_id = request.args.get('site_id')
		if not site_id:
			return jsonify(ApiError('missing query arg: site_id'))
		nodes = Node.query.filter(Node.site_id == site_id).all()
		if nodes:
			return jsonify({'objects': [node.json() for node in nodes]})
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(NodeListResource, '/nodes', '/node/all')


class SensorTypeResource(restful.Resource):
	def get(self, sensortype_id):
		sensortype = SensorType.query.filter_by(id = sensortype_id).first()
		if sensortype:
			return jsonify(ApiObjects(sensortype.json()))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def delete(self, sensortype_id):
		sensortype = SensorType.query.filter_by(id = sensortype_id).first()
		if sensortype:
			SensorType.delete(id = sensortype.id)
			return jsonify(ApiObjects(sensortype.json()))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def post(self):
		name = request.form.get('name', None)
		unit = request.form.get('unit', None)
		if not name:
			return jsonify(ApiError('missing form data: name'))
		if not unit:
			return jsonify(ApiError('missing form data: unit'))
		sensortype = SensorType.create(name = name, unit = unit)
		return jsonify(ApiObjects(sensortype.json()))	

rest_api.add_resource(SensorTypeResource, '/sensortype/<int:sensortype_id>', '/sensortype')


class SensorResource(restful.Resource):
	def get(self, sensor_id = None):
		sensor = Sensor.query.filter_by(id = sensor_id).first()
		if sensor:
			return jsonify(ApiObjects(sensor.json()))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def delete(self, sensor_id = None):
		sensor = Sensor.query.filter_by(id = sensor_id).first()
		if sensor:
			Sensor.delete(id = sensor.id)
			return jsonify(ApiObjects(sensor.json()))
		else:
			return jsonify(ApiObjects())

	
	@http_auth_required
	def post(self):
		args = {}
		
		node_id = request.form.get('node_id')
		if node_id: 
			node = Node.query.filter_by(id = node_id).first()
			if node: 
				args.update({'node' : node})
			else: 
				return jsonify(ApiError('node {} not found'.format(node_id)))
		else: 
			return jsonify(ApiError('missing form data: node_id'))

		sensortype_id = request.form.get('sensortype_id')
		if sensortype_id: 
			sensortype = SensorType.query.filter_by(id = sensortype_id).first()
			if sensortype: 
				args.update({'sensortype' : sensortype})
			else: 
				return jsonify(ApiError('sensortype {} not found'.format(sensortype_id)))
		else: 
			return jsonify(ApiError('missing form data: sensortype_id'))

		args.update({'name': request.form.get('name')})

		sensor = Sensor.create(**args)
		if sensor:
			return jsonify(ApiObjects(sensor.json()))
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(SensorResource, '/sensor/<int:sensor_id>', '/sensor')


class SensorListResource(restful.Resource):
	def get(self):
		node_id = request.args.get('node_id')
		if not node_id:
			return jsonify(ApiError('missing query arg: node_id'))
		sensors = Sensor.query.filter(Sensor.node_id == node_id).all()
		if sensors:
			return jsonify(ApiObjects([sensor.json() for sensor in sensors]))
		else: 
			return jsonify(ApiObjects())


rest_api.add_resource(SensorListResource, '/sensors')



def store_reading(sensor_id, value, timestamp):	
	try:
		sensor = Sensor.query.filter_by(id = sensor_id).first()
	except sqlalchemy.exc.DataError:
		return jsonify(ApiError('Invalid sensor_id: {}'.format(sensor_id)))
	if not sensor:
		return jsonify(ApiError('No such sensor: {}'.format(sensor_id)))
	
	try:
		value = float(value)
	except ValueError:
		return jsonify(ApiError('value could not be converted into float: {}'.format(value)))
	
	try:
		timestamp = datetime.fromtimestamp(float(timestamp))
	except (ValueError, TypeError):
		return jsonify(ApiError('timestamp not provided as epoch time: {}'.format(timestamp)))
	reading = Reading.create(sensor = sensor, value = value, timestamp = timestamp)
	return reading.id


class ReadingResource(restful.Resource):
	def get(self, reading_id = None):
		reading = Reading.query.filter_by(id = reading_id).first()
		if reading:
			return jsonify(ApiObjects(reading.json()))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def delete(self, reading_id = None):
		reading = Reading.query.filter_by(id = reading_id).first()
		if reading:
			reading.delete(id = reading.id)
			return jsonify(ApiObjects(reading.json()))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def post(self):
		sensor_id = request.form.get('sensor_id')
		value = request.form.get('value')
		timestamp = request.form.get('timestamp')
		
		if not value: 
			return jsonify(ApiError('missing value'))
		if not timestamp: 
			return jsonify(ApiError('missing timestamp'))
		if not sensor_id: 
			return jsonify(ApiError('missing sensor_id'))
		else:
			reading_id = store_reading(sensor_id, value, timestamp)
			return ApiObjects(reading_id)


rest_api.add_resource(ReadingResource, '/reading/<int:reading_id>', '/reading')




class ReadingListResource(restful.Resource):
	def get(self):
		sensor_id = request.args.get('sensor_id')
		if not sensor_id:
			return jsonify(ApiError('missing query arg: sensor_id'))
		readings = Reading.query.filter(Reading.sensor_id == sensor_id).all()
		if readings:
			return jsonify(ApiObjects([reading.json() for reading in readings]))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def post(self):
		format = request.args.get('format', 'json')
		if not format in ['json', 'compact']:
			return jsonify(ApiError('format arg must be either "json" or "compact"'))
		data = request.form.get('readings', None)
		if not data: 
			return jsonify(ApiError('data must be passed in the request body'))

		if format == 'compact':
			try:
				stored_readings = []
				for sensor_id, value, timestamp in map(lambda r: r.split(','), data.split(';')):
					reading_id = store_reading(sensor_id, value, timestamp)
					stored_readings.append(reading_id)
				return ApiObjects(stored_readings)
			except Exception:
				return jsonify(ApiError('Could not store data. Please submit data in the format "sensor_id,value,timestamp;sensor_id,value,timestamp;" etc.'))
		
		elif format == 'json':
			try:
				stored_readings = []
				readings = ujson.loads(data)
				print readings
				for reading in readings:
					sensor_id, value, timestamp = reading.get('sensor_id'), reading.get('value'), reading.get('timestamp')
					reading_id = store_reading(sensor_id, value, timestamp)
					stored_readings.append(reading_id)
				return ApiObjects(stored_readings)
			except Exception:
				return jsonify(ApiError('Please submit data as a JSON list of dict, like this: "[{"timestamp":1451394155.4250559807,"sensor_id":1,"value":99.0}]"'))


rest_api.add_resource(ReadingListResource, '/readings')
