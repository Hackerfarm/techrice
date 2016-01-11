from flask import request
from models import Reading, Sensor, Node
import time
from app import app
from datetime import datetime, timedelta
def get_sensor_period_data(sensor_id, start_datetime, end_datetime):
	data = Reading.query.filter((Reading.sensor_id == sensor_id) & (Reading.timestamp > start_datetime) & (Reading.timestamp < end_datetime)).all()
	xdata = map(lambda r: time.mktime(r.timestamp.timetuple()) * 1000, data)
	ydata = map(lambda r: r.value, data)
	# ydata = list(loggeobrowngen(len(xdata)))
	return xdata, ydata

def get_chart_settings():
	settings = {}
	settings.update({'width': request.args.get('width', 850)})
	settings.update({'height': request.args.get('height', 500)})
	settings.update({'color_category': request.args.get('color_category', 'category20b')})
	# settings.update({'color_category': request.args.get('height', 'category20b')})
	# settings.update({'color_category': request.args.get('height', 'category20b')})

	return settings


from nvd3 import lineChart
@app.route('/chart/weekly/sensor/<int:sensor_id>')
def sensor_weekly_chart(sensor_id):
	end_datetime = datetime.utcnow() + timedelta(hours = 9)
	start_datetime = end_datetime - timedelta(days = 7) + timedelta(hours = 9)
	sensor = Sensor.query.filter_by(id = sensor_id).first()
	if not sensor: 
		return "sensor {} not found".format(sensor_id)
	
	xdata, ydata = get_sensor_period_data(sensor_id, start_datetime, end_datetime)
	chart = lineChart(name="sensor {} weekly".format(sensor_id), x_is_date=True, x_axis_format="%b %d %a", **get_chart_settings())
	extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
	chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent

@app.route('/chart/daily/sensor/<int:sensor_id>')
def sensor_daily_chart(sensor_id):
	end_datetime = datetime.utcnow() + timedelta(hours = 9)
	start_datetime = end_datetime - timedelta(days = 7) + timedelta(hours = 9)
	sensor = Sensor.query.filter_by(id = sensor_id).first()
	if not sensor: 
		return "sensor {} not found".format(sensor_id)
	
	xdata, ydata = get_sensor_period_data(sensor_id, start_datetime, end_datetime)
	print xdata
	chart = lineChart(name="sensor {} daily".format(sensor_id), x_is_date=False, x_axis_format="AM_PM", **get_chart_settings())
	extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
	chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent


@app.route('/chart/weekly/node/<int:node_id>')
def node_weekly_chart(node_id):
	end_datetime = datetime.utcnow() + timedelta(hours = 9)
	start_datetime = end_datetime - timedelta(days = 7) + timedelta(hours = 9)
	node = Node.query.filter_by(id = node_id).first()
	if not node: return "node {} not found".format(node_id)
	chart_settings = get_chart_settings()
	chart = lineChart(name="node {} weekly".format(node_id), x_is_date=True, x_axis_format="%b %d %a", **chart_settings)
	for sensor in node.sensors:
		xdata, ydata = get_sensor_period_data(sensor.id, start_datetime, end_datetime)
		extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " calls"}, "date_format": "%d %b %Y %H:%M:%S %p"}
		chart.add_serie(y=ydata, x=xdata, name=sensor.name, extra=extra_serie)
	chart.buildhtml()
	return chart.htmlcontent