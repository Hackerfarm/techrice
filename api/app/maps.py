from flask import render_template, Markup, url_for

import uuid
from app import app
from models import Node

class NodeMarker(object):
	def __init__(self, longitude, latitude, icon_url = None, infowindow = None, click_redirect = "http://techrice.jp"):
		assert isinstance(longitude, float), 'longitude must be a float'
		assert isinstance(latitude, float), 'latitude must be a float'
		self.longitude = longitude
		self.latitude = latitude
		self.infowindow = Markup(infowindow)
		self.uuid = uuid.uuid4().hex

		assert click_redirect, 'click_redirect must be a url'
		self.click_redirect = click_redirect

	def __repr__(self):
		return str(self.__dict__)

@app.route("/map/nodes")
def nodes_map():
	nodes = Node.query.filter((Node.longitude != None) & (Node.latitude != None)).all()
	return make_map(nodes)

@app.route("/map/site/<int:site_id>")
def site_map(site_id):
	nodes = Node.query.filter((Node.site_id == site_id) & (Node.longitude != None) & (Node.latitude != None)).all()
	return make_map(nodes)

def make_map(nodes):
	markers = [NodeMarker(
		longitude = node.longitude, 
		latitude = node.latitude, 
		infowindow = '{} (id {})'.format(node.name, node.id), 
		click_redirect = '/chart/weekly/node/{}'.format(node.id)
		) for node in nodes]
	return Markup(render_template("gmap.html", markers = markers))
