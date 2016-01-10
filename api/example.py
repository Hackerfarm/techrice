import requests
import ujson
from random import random
import time
from datetime import datetime, timedelta
from termcolor import colored

host = 'http://localhost:8080/'
creds = ('dalekk@gmail.com', 'password')

def green(string):
	return colored(string, 'green')

if __name__ == '__main__':
	
	### Create a site
	response = requests.post(host + 'site', auth = creds, data = {'name': 'newsite'}).text
	site = ujson.loads(response)['objects']
	print green('created site: ') + str(site)

	

	### Create a node in that site
	response = requests.post(host + 'node', auth = creds, data = {'name': 'newnode', 'site_id' : site['id']}).text
	node = ujson.loads(response)['objects']
	print green('created node: ') + str(node)

	### Create a sensortypes for DHT11
	response = requests.post(host + 'sensortype', auth = creds, data = {'name': 'DHT11_temperature', 'unit': 'C'}).text
	temperature_sensortype = ujson.loads(response)['objects']
	print green('created sensortype: ') + str(temperature_sensortype)

	response = requests.post(host + 'sensortype', auth = creds, data = {'name': 'DHT11_humitidy', 'unit': '%'}).text
	humidity_sensortype = ujson.loads(response)['objects']
	print green('created sensortype: ') + str(humidity_sensortype)

	### Create sensors
	response = requests.post(host + 'sensor', auth = creds, data = {'node_id': node['id'], 'sensortype_id': temperature_sensortype['id']}).text
	temperature_sensor = ujson.loads(response)['objects']
	print green('created sensor: ') + str(temperature_sensor)

	### Now post some data to the API
	for i in range(10):
		response = requests.post(host + 'reading', auth = creds, data = {'sensor_id' : temperature_sensor['id'], 'value': 20 + 5 * random(), 'timestamp' : time.time()}).text
		print green('posted single reading: ') + str(ujson.loads(response)['objects'])
		# print ujson.loads(response)


	### Now try batch posting some data using COMPACT format (good for microcontrollers)
	### format: sensor_id,value,timestamp;sensor_id,value,timestamp etc
	readings = ";".join(['1,{},{}'.format(20 + 5 * random(), time.time()) for i in range(10)])
	# print 'posting multiple readings: ', readings
	response = requests.post(host + 'readings?format=compact', auth = creds, data = {'readings': readings}).text
	print green('posted multiple readings: '), str(ujson.loads(response))
