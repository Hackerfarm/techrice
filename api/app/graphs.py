from flask import request, jsonify
from models import Reading, Sensor, Node
import calendar
from app import app
from datetime import datetime, timedelta
from flask_restful import reqparse
from resources import ApiError

def get_sensor_period_data(sensor_id, start_datetime, end_datetime):
	#data = Reading.query.filter((Reading.sensor_id == sensor_id) & (Reading.timestamp > start_datetime) & (Reading.timestamp < end_datetime)).all()
	#xdata = map(lambda r: time.mktime(r.timestamp.timetuple()) * 1000, data)
	data = Reading.query.filter((Reading.sensor_id == sensor_id) & (Reading.created > start_datetime) & (Reading.created < end_datetime)).order_by(Reading.created).all()
	xdata = map(lambda r: calendar.timegm(r.created.timetuple()) * 1000, data)
	ydata = map(lambda r: r.value, data)
	# ydata = list(loggeobrowngen(len(xdata)))
	return xdata, ydata

def get_chart_settings():
	settings = {}
	settings.update({'width': request.args.get('width', '100%')})
	settings.update({'height': request.args.get('height', 700)})
	settings.update({'color_category': request.args.get('color_category', 'category20b')})
	# settings.update({'color_category': request.args.get('height', 'category20b')})
	# settings.update({'color_category': request.args.get('height', 'category20b')})

	return settings


from nvd3 import lineChart
@app.route('/graph/sensor/<int:sensor_id>')
def sensor_weekly_chart(sensor_id):
	end_datetime = datetime.utcnow() + timedelta(hours = 9)
	start_datetime = end_datetime - timedelta(days = 7) + timedelta(hours = 9)
	sensor = Sensor.query.filter_by(id = sensor_id).first()
	if not sensor: 
		return "sensor {} not found".format(sensor_id)
	
	xdata, ydata = get_sensor_period_data(sensor_id, start_datetime, end_datetime)
	chart_settings = get_chart_settings()
	chart = lineChart(name="sensor {} weekly".format(sensor_id), x_is_date=True, x_axis_format="%y %b %d %H:%M", **chart_settings)
	extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%y %d %b %Y %H:%M:%S %p"}
	chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent



@app.route('/graph/node/<int:node_id>')
def node_weekly_chart(node_id):
	parser = reqparse.RequestParser(bundle_errors = True)
	parser.add_argument('days', type=int, required=False, default = 0, help='<int> > 0 days')
	parser.add_argument('hours', type=int, required=False, default = 0, help='<int> > 0 hours')
	args = parser.parse_args()
	
	days = args['days']
	hours = args['hours']

	if days < 0 or hours < 0:
		return jsonify(ApiError('time parameters days >= 0 and hours >= 0 required'))
	
	if days == 0 and hours == 0:
		days = 1
	
	start_datetime = datetime.utcnow() - timedelta(days = days, hours = hours)
	end_datetime = datetime.utcnow()

	node = Node.query.filter_by(id = node_id).first()
	if not node: return "node {} not found".format(node_id)
	chart_settings = {'width': '100%', 'height': 500}
	chart = lineChart(name="node {} weekly".format(node_id), x_is_date=True, x_axis_format="%b %d %H:%M", **chart_settings)
	for sensor in node.sensors:
		xdata, ydata = get_sensor_period_data(sensor.id, start_datetime, end_datetime)
		extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
		chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
	chart.buildhtml()
	# return chart
	return chart.htmlcontent

def testchart(node_id):
	end_datetime = datetime.utcnow() + timedelta(hours = 9)
	start_datetime = end_datetime - timedelta(days = 7) + timedelta(hours = 9)
	node = Node.query.filter_by(id = node_id).first()


	if not node: return "node {} not found".format(node_id)
	chart_settings = {'width': '100px', 'height': 500}
	chart = lineChart(name="node {} weekly".format(node_id), x_is_date=True, x_axis_format="%b %d %H:%M", **chart_settings)
	
	x = range(10)
	s1 = [random() for r in range(10)]
	s2 = [10 + random() for r in range(10)]

	a1 = chart.new_x_axis(name = 'percent', tickFormat = u"d3.format(',.02f')")
	a2 = chart.new_x_axis(name = 'temperature', tickFormat = u"d3.format(',.02f')")
	for sensor in node.sensors:
		xdata, ydata = get_sensor_period_data(sensor.id, start_datetime, end_datetime)
		extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
		chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
	chart.buildhtml()
	return chart
	return chart.htmlcontent


# @app.route('/chart/daily/sensor/<int:sensor_id>')
# def sensor_daily_chart(sensor_id):
# 	end_datetime = datetime.utcnow() + timedelta(hours = 9)
# 	start_datetime = end_datetime - timedelta(days = 7) + timedelta(hours = 9)
# 	sensor = Sensor.query.filter_by(id = sensor_id).first()
# 	if not sensor: 
# 		return "sensor {} not found".format(sensor_id)
	
# 	xdata, ydata = get_sensor_period_data(sensor_id, start_datetime, end_datetime)
# 	print xdata
# 	chart = lineChart(name="sensor {} daily".format(sensor_id), x_is_date=False, x_axis_format="AM_PM", **get_chart_settings())
# 	extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
# 	chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
# 	chart.buildhtml()
# 	return chart.htmlcontent


