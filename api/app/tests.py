import requests
import ujson
import datetime
def assert_site_json(site_json):
	try:
		site = ujson.loads(site_json)
	except:
		assert False
	assert site.has_key('id')
	assert isinstance(site['id'], int)
	assert site.has_key('alias')
	assert isinstance(site['alias'], unicode)
	assert site.has_key('nodes')
	assert isinstance(site['nodes'], list)
	assert site.has_key('type')
	assert site['type'] == 'site'
	assert site.has_key('created')
	assert datetime.fromtimestamp(site['created'])
	assert site.has_key('updated')
	assert datetime.fromtimestamp(site['updated'])

def assert_node_json(node_json):
	try:
		node = ujson.loads(node_json)
	except:
		assert False
	assert node.has_key('id')
	assert isinstance(node['id'], int)
	assert node.has_key('site_id') or not node['site_id']
	assert isinstance(node['site_id'], int)
	assert node.has_key('alias')
	assert isinstance(node['alias'], unicode)
	assert node.has_key('nodetype_id')
	assert isinstance(node['nodetype_id'], int) or not node['nodetype_id']
	assert node.has_key('sensors')
	assert isinstance(node['sensors'], list)
	assert node.has_key('latitude')
	assert isinstance(node['latitude'], float)
	assert node.has_key('longitude')
	assert isinstance(node['longitude'], float)
	assert node.has_key('type')
	assert node['type'] == 'site'
	assert node.has_key('created')
	assert datetime.fromtimestamp(float(node['created']))
	assert node.has_key('updated')
	assert datetime.fromtimestamp(float(node['updated']))

class TestResources:
	url = 'http://localhost:8080/'

	def test_site_get(self):
		r = requests.get(url)
		assert r.ok
		r = ujson.loads(r.text)
		assert r.has_key('objects')
		assert len(r['objects']) == 1
		# assert r['objects']

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
