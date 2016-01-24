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

@app.route('/posttest', methods = ['POST'])
def posttest():
	return str(request.form)

from flask.ext.security import http_auth_required
import seed
@app.route('/seed/node/techrice')
@http_auth_required
def seed_techrice_node():
	return jsonify(seed.seed_techrice_node())

