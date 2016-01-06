from app import app
from flask.ext.security import login_required



# @app.route('/', methods = ['GET'])
@login_required
def index():
	return 'Unauthorized'

@app.route('/unauthorized')
def unauthorized():
	return 'Go away'