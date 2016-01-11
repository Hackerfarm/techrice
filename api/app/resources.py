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
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('name', type=str, location='form', required=True, help='<str> name required')
		args = parser.parse_args()
		site = Site.create(name = args['name'])
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

from flask_restful import reqparse


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
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('site_id', type=int, location='form', required=True, help='<int> site_id required')
		parser.add_argument('name', type=str, location='form', required=True, help='<str> name required')
		parser.add_argument('longitude', type=float, location='form', required=True, help='<float> longitude required')
		parser.add_argument('latitude', type=float, location='form', required=True, help='<float> latitude required')
		args = parser.parse_args()
		
		site = Site.query.filter_by(id = args['site_id']).first()
		if not site:
			return jsonify(ApiError('site {} not found'.format(args['site_id'])))

		node = Node.create(site = args['site'], name = args['name'], longitude = args['longitude'], latitude = args['latitude'])
		if node:
			return jsonify(ApiObjects(node.json()))
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(NodeResource, '/node/<int:node_id>', '/node')


class NodeListResource(restful.Resource):
	def get(self):		
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('site_id', type=int, location='form', required=True, help='<int> site_id required')
		args = parser.parse_args()

		site_id = args['site_id']
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
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('name', type=str, location='form', required=True, help='<str> name required')
		parser.add_argument('unit', type=str, location='form', required=True, help='<str> unit required')
		args = parser.parse_args()
		sensortype = SensorType.create(name = args['name'], unit = args['unit'])
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
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('node_id', type=int, location='form', required=True, help='<int> node_id required')
		parser.add_argument('sensortype_id', type=int, location='form', required=True, help='<int> sensortype_id required')
		parser.add_argument('name', type=int, location='form', required=False, help='<int> sensortype_id optional')
		args = parser.parse_args()

		node = Node.query.filter_by(id = args['node_id']).first()
		if not node: 
			return jsonify(ApiError('node {} not found'.format(args['node_id'])))

		sensortype = SensorType.query.filter_by(id = args['sensortype_id']).first()
		if not sensortype: 
			return jsonify(ApiError('sensortype {} not found'.format(args['sensortype_id'])))

		sensor = Sensor.create(node = args['node'], sensortype = args['sensortype'], name = args['name'])
		if sensor:
			return jsonify(ApiObjects(sensor.json()))
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(SensorResource, '/sensor/<int:sensor_id>', '/sensor')


class SensorListResource(restful.Resource):
	def get(self):
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('node_id', type=int, required=True, help='<int> node_id required')
		args = parser.parse_args()
		
		sensors = Sensor.query.filter(Sensor.node_id == args['node_id']).all()
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
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('sensor_id', type=int, location='form', required=True, help='<int> sensor_id required')
		parser.add_argument('value', type=float, location='form', required=True, help='<float> value required')
		parser.add_argument('timestamp', type=float, location='form', required=True, help='<float> epoch timestamp required')
		args = parser.parse_args()

		sensor = Sensor.query.filter_by(id = args['sensor_id']).first()
		if not sensor:
			return jsonify(ApiError('sensor {} not found'.format(args['sensor_id'])))
		
		reading = Reading.create(sensor = sensor, value = args['value'], timestamp = args['timestamp'])
		return jsonify(ApiObjects(reading.json()))


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
