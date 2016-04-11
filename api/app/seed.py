from random import random
import time
from datetime import datetime, timedelta
from models import Site, Node, SensorType, Sensor, Reading
from jinja2 import Template
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

class TechRice(object):
	header = """
typedef struct{
  reading_t temperature;
  reading_t humidity;
  reading_t battery;
  reading_t solar;
  int32_t count;
  int32_t signal_strength;
  char timestamp[19];
  int32_t node_id;
} techrice_packet_t;

/*
These values will be provided by the API
*/
#define NODE_ID {{ node_id }}
#define TEMPERATURE_SENSOR_ID {{ temperature_sensor_id }}
#define HUMIDITY_SENSOR_ID {{ humidity_sensor_id }}
#define BATTERY_SENSOR_ID {{ battery_sensor_id }}
#define SOLAR_SENSOR_ID {{ solar_sensor_id }}
#define SONAR_SENSOR_ID {{ sonar_sensor_id }}

techrice_packet_t r = {
  {TEMPERATURE_SENSOR_ID,0}, 
  {HUMIDITY_SENSOR_ID,0},
  {BATTERY_SENSOR_ID,0}, 
  {SOLAR_SENSOR_ID,0},
  0,
  0,
  "",
  NODE_ID
};
"""
	@staticmethod
	def seed_nodetypes():
		try:
			SensorType.create(name = 'battery voltage', unit = 'mV')
			SensorType.create(name = 'solar voltage', unit = 'mV')
			SensorType.create(name = 'DHT11 temperature', unit = 'C')
			SensorType.create(name = 'DHT11 humidity', unit = '%')
			SensorType.create(name = 'HC SR-04', unit = 'cm')
		except IntegrityError:
			db.session.rollback()
			return 'Seems like the sensortypes have already been created. Session has been rolled back'

	@staticmethod
	def seed_node(site_id = None, alias = None, latitude = None, longitude = None):
		if site_id:
			site = Site.query.filter_by(id = site_id).first()
		else:
			site = Site.create(name = 'Techrice site {}'.format(uuid4().hex))
		
		if not alias: 
			alias = 'Techrice node {}'.format(uuid4().hex)
		node = Node.create(name = alias, site = site, latitude = latitude, longitude = longitude)
		

		solar = Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'solar voltage').first(), name = 'vsol')
		battery = Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'battery voltage').first(), name = 'vbat')
		temperature = Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'DHT11 temperature').first(), name = 'temperature')
		humidity = Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'DHT11 humidity').first(), name = 'humidity')
		sonar = Sensor.create(node = node, sensortype = SensorType.query.filter_by(name = 'sonar HC SR-04').first(), name = 'sonar')

		header = Template(TechRice.header).render(**{
		  'node_id': node.id,
		  'temperature_sensor_id': temperature.id,
		  'humidity_sensor_id':humidity.id,
		  'battery_sensor_id': battery.id,
		  'solar_sensor_id': solar.id,
		  'sonar_sensor_id': sonar.id})

		return {
			'node': 'name: {}, id: {}, longitude: {}, latitude: {}'.format(node.name, node.id, node.longitude, node.latitude),
			'sensors': map(lambda s: 'name: {}, id: {}'.format(s.name, s.id), node.sensors),
			'header' : header
			}


from jinja2.filters import do_capitalize
class Header(object):
	template = """
typedef struct{
  {% for sensor in sensors -%}
  reading_t {{sensor['name']}};
  {% endfor -%}
  int32_t count;
  int32_t signal_strength;
  char timestamp[19];
  int32_t node_id;
} packet_t;

#define NODE_ID {{node_id}}
{% for sensor in sensors -%}
#define {{sensor['name']|upper}}_SENSOR_ID {{sensor['id']}};
{% endfor %}

techrice_packet_t r = {
  {% for sensor in sensors -%}
  {%raw%}{{%endraw%}{{sensor['name']|upper}}_SENSOR_ID{%raw%}}, 0{%endraw%},
  {% endfor -%}
  0,
  0,
  "",
  NODE_ID
};
"""

	@staticmethod
	def get_header(node_id):
		node = Node.query.filter_by(id = node_id).first()
		if node:
			sensors = [{'name': sensor.name.replace(' ', '_'), 'id': sensor.id} for sensor in node.sensors]
		else:
			return 'node not found'
		header = Template(Header.template).render(node_id = node_id, sensors = sensors)
		return header



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
