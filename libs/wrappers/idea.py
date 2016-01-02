import time


class Board(object):
	def __init__(self, node_id, sensors):
		self.node_id = node_id
		self.sensors = sensors

	def read_sensors(self):
		for sensor in self.sensors:
			measurements = sensor.read()
			for sensor_id, value in measurements.items():
				timestamp = time.time()
				r = Reading(self.node_id, sensor_id, value, timestamp)

class Sensor(object):
	pass

class DHT11(Sensor):
	def __init__(self, temperature_sensor_id, humidity_sensor_id):
		self.temperature_sensor_id = temperature_sensor_id
		self.humidity_sensor_id = humidity_sensor_id

	def read(self):
		return {self.temperature_sensor_id: self.dht.temperature,
				self.humidity_sensor_id: self.dht.humidity}
