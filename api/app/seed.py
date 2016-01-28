from random import random
import time
from datetime import datetime, timedelta
from models import Site, Node, SensorType, Sensor, Reading

import itertools
import math
from random import normalvariate
def loggeobrowngen(n = -1, offset = 50):
	p = 1
	dt = 0.5
	mu = 0
	sigma = 1
	# for i in itertools.repeat(1, times = n):
	while True:
		p *= math.exp((mu - sigma * sigma // 2) * dt +sigma * normalvariate(0, dt * dt))
		yield math.log(p) + offset


def seed_site(sensors = 1, days = 7, interval_seconds = 3600):
	site = Site.create(name = 'seeded_site')
	node = Node.create(name = 'seeded_node', site = site, latitude = 35.146623 + random() / 100.0, longitude = 139.9835682 + random() / 100.0)
	sensortype = SensorType.create(name = 'HC SR-04', unit = 'cm')
	for i in range(sensors):
		sensor = Sensor.create(sensortype = sensortype, node = node, name = 'water distance %s'%i)
		timestamp = datetime.utcnow() - timedelta(days = 7)
		data = loggeobrowngen()
		n_readings = 0
		while timestamp < datetime.utcnow():
			Reading.create(sensor = sensor, value = data.next(), timestamp = timestamp)
			timestamp += timedelta(seconds = interval_seconds)
			n_readings += 1
		data.close()
	return {'site': site, 'node': node}

from uuid import uuid4

from app import db
from sqlalchemy.exc import IntegrityError

def seed_techrice_nodetypes():
	try:
		SensorType.create(name = 'battery voltage', unit = 'mV')
		SensorType.create(name = 'solar voltage', unit = 'mV')
		SensorType.create(name = 'DHT11 temperature', unit = 'C')
		SensorType.create(name = 'DHT11 humidity', unit = '%')
		SensorType.create(name = 'sonar HC SR-04', unit = 'cm')
	except IntegrityError:
		db.session.rollback()
		return 'Seems like the sensortypes have already been created. Session has been rolled back'

def seed_techrice_node(site_id = None):
	if site_id:
		site = Site.create(name = 'Techrice site {}'.format(uuid4().hex))
	else:
		site = Site.query.filter_by(id = site_id)
	node = Node.create(name = 'Techrice node {}'.format(uuid4().hex), site = site)
	

	Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'solar voltage').first(), name = 'vsol')
	Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'battery voltage').first(), name = 'vbat')
	Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'DHT11 temperature').first(), name = 'temperature')
	Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'DHT11 humidity').first(), name = 'humidity')
	Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'sonar HC SR-04').first(), name = 'distance to water surface')
	return {'node': 'name: {}, id: {}'.format(node.name, node.id), 'sensors': map(lambda s: 'name: {}, id: {}'.format(s.name, s.id), node.sensors)}

	# vbat_sensortype = SensorType.query.filter_by(name = 'vbat').first()
	# dht11_temp_sensortype = SensorType.query.filter_by(name = 'DHT11 temperature').first()
	# dht11_humidity_sensortype = SensorType.query.filter_by(name = 'DHT11 humidity').first()
	# sonar_sensortype = SensorType.query.filter_by(name = 'HC SR-04').first()


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
			self.sensor = Sensor.create(name = 'started at %s'%datetime.utcnow().ctime())
			print '*********** Created new sensor'
			print self.sensor

	def run(self):
		for value in loggeobrowngen():
			reading = Reading.create(sensor = self.sensor, value = value, timestamp = datetime.now())
			print reading
			time.sleep(self.wait_interval)
