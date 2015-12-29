import serial
import os
import re
import requests
import time
import sys
from Queue import Queue, Full
from threading import Thread, Event
from logging import Logger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
from argparse import ArgumentParser
from datetime import datetime
import zlib
import json

logger = Logger(__name__)
filehandler = RotatingFileHandler('log.txt', maxBytes = 10**6)
streamhandler = StreamHandler(sys.stdout)
formatter = Formatter('%(asctime)s - %(thread)d - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
streamhandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)



def open_serial_device():
	def open_device(device_name):
		logger.debug('Device name: %s'%device_name)
		try:
			logger.info('Trying to open device %s'%device_name)
			device = serial.Serial(device_name, BAUDRATE, timeout = 1)
			if device.isOpen():
				logger.info('Device %s is open.'%device_name)
				logger.info(device)
				return device
			else:
				os._exit(1)
		except OSError:
			os._exit(1)


	if DEVICE_NAME:
		device = open_device(DEVICE_NAME)
		if device:
			return device
		else:
			logger.warning('Failed to open device %s. Trying other devices...'%DEVICE_NAME)	
	else:
		available_linux_devices = filter(lambda x: re.match('tty.usb*', x) or re.match('ttyUSB*', x), os.listdir('/dev'))
		if len(available_linux_devices) > 0:
			device =  open_device('/dev/' + available_linux_devices[0])
		else:
			default_windows_device = 'COM4'
			device = open_device(default_windows_device)
		if not device: 
			logger.fatal("Couldn't find connected Chibi boards. Are you sure it's plugged in? :)")
			os._exit(1)

		

def parse_reading(reading):
	if reading == "": return []

	try:
		addr, payload = reading.split('@')
		addr = addr[1:]
		if addr == 0:
			logger.warning('Discarding data from invalid node 0')
			return []
		parsed = map(lambda y: dict(zip(['alias', 'value', 'timestamp'], y)), map(lambda x: x.split(':'), payload[:-3].split(';')))
                logger.info('Parsed %s readings.'%len(parsed))
		for p in parsed:
			logger.debug("Reading from node %s: %s."%(addr, p))
			p.update({'node_id':addr})
			p.update({'timestamp':datetime.now().strftime('%Y-%m-%d-%H:%M:%S:%f')})
		return parsed 
	except ValueError:
		logger.exception('Recieved garbage from serial port.')
		return []
	


def read_serial(name, is_running):
	logger.debug('Running %s daemon'%name)
	serial_connection = open_serial_device()

	previous_reading = ''

	while is_running.isSet():
		if not is_running.isSet(): 
			logger.info('%s got KILL signal! Please wait.'%name)
		try:
			reading = serial_connection.readline()
			logger.debug('From serial: %s'%reading)
		except ValueError:
			message = 'Problem reading serial port. Please try to run the program again!'	
			logger.fatal(message)
			os._exit(1)

		### If the current reading is the same as the previous reading, there is no reason to send it to the Internet
		if reading != previous_reading:
			previous_reading = reading
			parsed_reading = parse_reading(reading)
			for i, p in enumerate(parsed_reading):
				try:
					queue.put_nowait(p)
				except Full:
					for i in range(10):
						discarded_reading = queue.get_nowait()
					queue.put_nowait(p)
					try:
						logger.warning('Full queue. Discarding data: %s'%(queue.qsize(), discarded_reading))
					except TypeError:
						logger.warning('Full queue. Discarded old data.')
		logger.debug('Data from serial: %s'%reading)

	logger.info("Closing serial port...")
	serial_connection.close()
	logger.info("Serial port closed.")


def get_timeout(data_size):
        return 0.1 * float(data_size)


def upload_daemon(name, is_running):
	logger.debug('Running %s daemon'%name)
	while is_running.isSet():
		print 'waiting in uploader'
		if not is_running.isSet(): 
			logger.info('%s got KILL signal! Please wait.'%name)
			return 

		if queue.empty():
			time.sleep(UPLOAD_INTERVAL)
			logger.debug('Sleeping %s seconds'%UPLOAD_INTERVAL)
		else:
			request_payload = prepare_data_in_queue()
			compressed_payload = compress_data(request_payload)
			data_size = sys.getsizeof(compressed_payload)
			timeout = get_timeout(data_size)

			try:
				data_hash = hash(frozenset(map(frozenset, request_payload)))
				logger.info("Data hash: %s (Attempt upload). Bytes: %s. Timeout is %f seconds."%(data_hash, data_size, data_size))
				response = requests.post(URL, data = compressed_payload, timeout = timeout)
				if response.ok:
					logger.info("Data hash: %s (Upload SUCCESS, status code: %s)."%(data_hash, response.status_code))
				else:
					logger.info("Data hash: %s (Upload FAILURE). Qsize: %s, status_code: %s"%(data_hash, queue.qsize(), response.status_code))                
				response.close()
			except requests.ConnectionError:
				logger.warning('ConnectionError. Discarding %s bytes of data.'%data_size)
			except requests.Timeout:
				logger.warning('Timeout. Discarding %s bytes of data.'%data_size)		
			
                

def compress_data(json_data):
	return zlib.compress(json.dumps(json_data))


def prepare_data_in_queue():
	request_payload = list()
	for i in range(queue.qsize()):
		request_payload.append(queue.get_nowait())
	return request_payload


def get_url(node_id, sensor_alias):
	return 'http://%s:%s/reading/node_%s/%s'%(HOST, PORT, node_id, sensor_alias)

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('--host', help = 'Server IP address e.g., 107.170.251.142', default = '128.199.191.249')
	parser.add_argument('--port', help = 'Port on the server (usually 80)', default = 80)
	parser.add_argument('--baud','-b', help = 'Serial port baud rate (default 57600)', default = 57600)
	parser.add_argument('--queue_size','-q', help = 'The size of the queue that functions as a buffer between Serial-to-Internet (default 10000)', default = 10000)
	parser.add_argument('--upload_interval', '-u', help = 'Interval in seconds between uploading to the server (default 60)', default = 60)
	parser.add_argument('--debug_level', '-l', help = 'Debug level', default = 'INFO', choices = ('DEBUG', 'INFO', 'WARNING', 'ERROR'))
	parser.add_argument('--serial_device', '-d', help = 'On Linux/OSX this is typically /dev/ttyUSB-something, and on Windows COM-something.')

	args = parser.parse_args()

	try:
		QUEUE_MAXSIZE = int(args.queue_size)
	except ValueError:
		logger.critical("Please specify an integer for the queue size")
		os._exit(1)

	HOST = args.host
	
	try:
		PORT = int(args.port)
	except ValueError:
		logger.critical("Please specify a port with an integer")
		os._exit(1)

	try:	
		BAUDRATE = int(args.baud)
	except ValueError:
		logger.critical("Please specify the baudrate of the serial port with an integer")
		os._exit(1)

	try:
		UPLOAD_INTERVAL = int(args.upload_interval)
	except ValueError:
		logger.critical("Please specify the the number of seconds to wait between uploading data to the host as an integer")
		os._exit(1)

	try:
		logger.setLevel(args.debug_level)	
	except ValueError:
		logger.critical("Please specify a valid debug level (DEBUG, INFO, WARNING, etc.)")
		os._exit(1)

	try:
		DEVICE_NAME = args.serial_device
	except ValueError:
		logger.critical("Could not parse argument --serial_device")
		os._exit(1)

	URL = 'http://%s:%s/readings'%(HOST, PORT)

	queue = Queue(QUEUE_MAXSIZE)
	
	logger.info('*******************************************************\n')
	logger.info('Process id: %s', os.getpid())
		
	is_running = Event()
	is_running.set()
	
	serial_reader = Thread(target = read_serial, args = ('Serial reader', is_running), name = 'SERIAL READER')
	serial_reader.start()

	if HOST:
		uploader = Thread(target = upload_daemon, args = ('Data sender', is_running), name = 'UPLOADER')
		uploader.daemon = True
		uploader.start()
	else:
		logger.warning('ATTENTION: Running without remote host, so no data is being sent to server!')
	
	try:
		while True:
			time.sleep(0.1)
	except KeyboardInterrupt:
		logger.info('Detected keyboard interrupt. Terminating Daemons. Please wait.')
		is_running.clear()