from app import rest_api

from flask import request, jsonify
import ujson
from flask.ext import restful

from models import Site, Node, NodeType, Sensor, SensorType, Reading

import sqlalchemy
from datetime import datetime

from flask.ext.security import login_required, http_auth_required
from flask_restful import reqparse


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

		node = Node.create(site = site, name = args['name'], longitude = args['longitude'], latitude = args['latitude'])
		if node:
			return jsonify(ApiObjects(node.json()))
		else:
			return jsonify(ApiObjects())

rest_api.add_resource(NodeResource, '/node/<int:node_id>', '/node')


class NodeListResource(restful.Resource):
	def get(self):		
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('site_id', type=int, required=True, help='<int> site_id required')
		args = parser.parse_args()
		
		nodes = Node.query.filter(Node.site_id == args['site_id']).all()
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

		sensor = Sensor.create(node = node, sensortype = sensortype, name = args['name'])
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
		parser = reqparse.RequestParser(bundle_errors = True)
		parser.add_argument('sensor_id', type=int, required=True, help='<int> sensor_id required')
		args = parser.parse_args()
		readings = Reading.query.filter(Reading.sensor_id == args['sensor_id']).all()
		if readings:
			return jsonify(ApiObjects([reading.json() for reading in readings]))
		else:
			return jsonify(ApiObjects())

	@http_auth_required
	def post(self):
		parser = reqparse.RequestParser(bundle_errors = True)		
		parser.add_argument('format', type=str, required = True, choices = ['json', 'compact'], help='<str> data format [json|compact]')
		parser.add_argument('readings', type=str, required = True, help='<str> multiple readings')
		parser.add_argument('node_id', type=int, help='<int> node_id required')
		parser.add_argument('timestamp', type=str, location = 'form', required = False, help='<str> timestamp required. Format: %Y-%m-%d %H:%M:%S')
		args = parser.parse_args()
		stored_readings = list()
		if args['format'] == 'compact':
			try:
				timestamp = '20' + args['timestamp']	
				timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
			except (ValueError, TypeError):
				timestamp = datetime.utcnow()
				#return jsonify(ApiError('could not parse timestamp: {}'.format(args['timestamp'])))

			try:
				readings = args['readings'].split(';')
				unpacked = map(lambda r: tuple(r.split(',')), readings)
				for r in unpacked: assert len(r) == 2
			except Exception:
				return jsonify(ApiError('Could not store data. Please submit data in the format "sensor_id,value;sensor_id,value;..."'))	

			# node = Node.query.filter_by(id = args['node_id']).first()
			# if not node:
			# 	return jsonify(ApiError('no such node: {}'.format(args['node_id'])))

			for sensor_id, value in unpacked:
				try:
					sensor_id = int(sensor_id)
				except ValueError:
					return jsonify(ApiError('could not convert sensor_id into integer: {}'.format(sensor_id)))
				sensor = Sensor.query.filter_by(id = sensor_id).first()
				if not sensor:
					return jsonify(ApiError('sensor {} not found'.format(sensor_id)))
				try:
					value = float(value)
				except ValueError:
					return jsonify(ApiError('value could not be converted to a number: {}'.format(value)))
				reading = Reading.create(sensor = sensor, value = value, timestamp = timestamp)
				stored_readings.append(reading.json())
			return jsonify(ApiObjects(stored_readings))

	# @http_auth_required
	# def post(self):
	# 	parser = reqparse.RequestParser(bundle_errors = True)		
	# 	parser.add_argument('format', type=str, required = True, choices = ['json', 'compact'], help='<str> data format [json|compact]')
	# 	parser.add_argument('readings', type=str, location = 'form', required = True, help='<str> multiple readings')
	# 	args = parser.parse_args()
		
	# 	if args['format'] == 'compact':
	# 		try:
	# 			readings = args['readings'].split(';')
	# 			unpacked = map(lambda r: tuple(r.split(',')), readings)
	# 			for r in unpacked: assert len(r) == 3
	# 		except Exception:
	# 			return jsonify(ApiError('Could not store data. Please submit data in the format "sensor_id,value,timestamp;sensor_id,value,timestamp;" etc.'))	
	# 	elif args['format'] == 'json':
	# 		try:				
	# 			readings = ujson.loads(args['readings'])
	# 			unpacked = [(r['sensor_id'], r['value'], r['timestamp']) for r in readings]
	# 		except Exception:
	# 			return jsonify(ApiError('Please submit data as a JSON serialized list of dict, like this: "[{"timestamp":1451394155.4250559807,"sensor_id":1,"value":99.0}]"'))

	# 	stored_readings = []
		
	# 	for sensor_id, value, timestamp in unpacked:
	# 		sensor = Sensor.query.filter_by(id = sensor_id).first()
	# 		if not sensor:
	# 			return jsonify(ApiError('sensor {} not found'.format(sensor_id)))
	# 		try:
	# 			value = float(value)
	# 		except ValueError:
	# 			return jsonify(ApiError('value could not be converted to float: {}'.format(value)))
	# 		try:
	# 			timestamp = float(timestamp)
	# 		except ValueError:
	# 			return jsonify(ApiError('timestamp could not be converted to float {}'.format(timestamp)))
	# 		reading = Reading.create(sensor = sensor, value = value, timestamp = timestamp)
	# 		stored_readings.append(reading.json())
	# 	return jsonify(ApiObjects(stored_readings))

rest_api.add_resource(ReadingListResource, '/readings')
