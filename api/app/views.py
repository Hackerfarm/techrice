from app import app
from flask.ext.security import login_required
from flask import request, jsonify


# @app.route('/', methods = ['GET'])
@login_required
def index():
	return 'Unauthorized'

@app.route('/unauthorized')
def unauthorized():
	return 'Go away'


@app.route('/testtest', methods = ['GET', 'POST'])
def testtest():
	return str(request.form)

from flask.ext.security import http_auth_required
from seed import TechRice
from flask_restful import reqparse

@app.route('/utcnow')
def get_utcnow():
	pass

from seed import Header
@app.route('/utils/node_header/<int:node_id>', methods = ['GET'])
def get_header(node_id):
	return jsonify({'header': Header.get_header(node_id)})


@app.route('/seed/node/techrice', methods = ['POST'])
@http_auth_required
def seed_techrice_node():
	parser = reqparse.RequestParser(bundle_errors = True)
	parser.add_argument('site_id', type=str, required=False, help='<str> site_id required. If site exists, please create one by HTTP POST /site')
	parser.add_argument('longitude', type=float, required=False, help='<float> node longitude')
	parser.add_argument('latitude', type=float, required=False, help='<float> node latitude')
	args = parser.parse_args()
	return jsonify(TechRice.seed_node(**args))
