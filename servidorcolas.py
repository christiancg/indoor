import pika
import threading
import traceback
import jsonpickle
from logger import Logger
log = Logger(__name__)

from modelos import Usuario

from flask import jsonify
import json
from CustomJSONEncoder import CustomJSONEncoder
encoder = CustomJSONEncoder()

def devolverJson(dj, msg, code):
	if msg is None:
		return Respuesta(code, jsonify({}))
	else:
		devolver = json.dumps(encoder.default(msg))
		return Respuesta(code, devolver)

class ServidorCola(threading.Thread):
	connection = None
	channel = None
	app = None
	endpoints = None
	
	def __init__(self, direccion, app, endpoints):
		threading.Thread.__init__(self)
		credentials = pika.PlainCredentials('test', 'ratablanca')
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=direccion, credentials=credentials))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue='rpc_queue')
		self.app = app
		self.endpoints = endpoints
		
	def _checkPermission(self, user, password):
		try:
			usr = Usuario.query.filter(Usuario.nombre == user).first()
			if usr is None:
				return False
			elif usr.password != password:
				return False
			else:
				return True
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False
	
	def _routeRequest(self, obj):
		if obj['Endpoint'] == 'obtenerConfiguraciones':
			dj, msg, code = self.endpoints.getConfig()
			return devolverJson(dj, msg, code)
		return jsonpickle.encode(Respuesta(200, {}))

	def processMessage(self, message):
		with self.app.app_context():
			print(str(message))
			try:
				msgObj = jsonpickle.decode(message)
				if self._checkPermission(msgObj['User'], msgObj['Password']):
					return jsonpickle.encode(self._routeRequest(msgObj))
				else:
					return jsonpickle.encode(Respuesta(401, { 'status':'Could not verify your access level for that URL.\n You have to login with proper credentials'}))
			except Exception, ex:
				log.exception(ex)
				print traceback.format_exc()
				return jsonpickle.encode(Respuesta(500, ex))

	def on_request(self, ch, method, props, body):
		try:
			response = self.processMessage(body)
			
			ch.basic_publish(exchange='',
							routing_key=props.reply_to,
							properties=pika.BasicProperties(correlation_id = props.correlation_id),
							body=str(response))
			ch.basic_ack(delivery_tag = method.delivery_tag)
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()

	def run(self):
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(self.on_request, queue='rpc_queue')
		print(" [x] Awaiting RPC requests")
		log.info(" [x] Awaiting RPC requests")
		self.channel.start_consuming()
		
class Respuesta(object):
	StatusCode = 0
	Success = False
	Result = {}
	def __init__(self, statusCode, result):
		self.StatusCode = statusCode
		if statusCode >= 200 and statusCode < 300:
			self.Success = True
		else:
			self.Success = False
		self.Result = result
