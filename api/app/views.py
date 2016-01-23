from app import app
from flask.ext.security import login_required
from flask import request


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
