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

def makeResponse(dj, msg, code):
	if msg is None:
		return Respuesta(code, jsonify({}))
	elif dj:
		devolver = json.dumps(encoder.default(msg))
		return Respuesta(code, devolver)
	else:
		return Respuesta(code, msg)

class ServidorCola(threading.Thread):
	connection = None
	channel = None
	app = None
	endpoints = None
	queueName = None
	
	def __init__(self, queueUrl, queueName, queueUser, queuePassword, app, endpoints):
		threading.Thread.__init__(self)
		credentials = pika.PlainCredentials(queueUser, queuePassword)
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=queueUrl, credentials=credentials))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=queueName)
		self.app = app
		self.endpoints = endpoints
		self.queueName = queueName
		
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
			return makeResponse(dj, msg, code)
		elif obj['Endpoint'] == 'obtenerImagen':
			dj, msg, code = self.endpoints.obtenerImagenIndoor()
			return makeResponse(dj, msg, code)
		elif obj['Endpoint'] == 'obtenerEventosPorFecha':
			fechaInicio= obj['GetParameters'][0] 
			fechaFin= obj['GetParameters'][1] 
			try:
				tipoEvento = obj['GetParameters'][2]
			except IndexError:
				tipoEvento = ''
			dj, msg, code = self.endpoints.obtenerEventosPorFecha(fechaInicio, fechaFin, tipoEvento)
			return makeResponse(dj, msg, code)	
		elif obj['Endpoint'] == 'obtenerProgramaciones':
			dj, msg, code = self.endpoints.obtenerProgramaciones()
			return makeResponse(dj, msg, code)
		elif obj['Endpoint'] == 'humedadYTemperatura':
			dj, msg, code = self.endpoints.humedadYTemperatura()
			return makeResponse(dj, msg, code)
		elif obj['Endpoint'] == 'agregarProgramacion':
			dataDict = json.loads(obj['JsonBodyContent'])
			dj, msg, code = self.endpoints.addProgramacion(dataDict)
			return makeResponse(dj, msg, code)	
		elif obj['Endpoint'] == 'editarProgramacion':
			dataDict = json.loads(obj['JsonBodyContent'])
			dj, msg, code = self.endpoints.editarProgramacion(dataDict)
			return makeResponse(dj, msg, code)
		elif obj['Endpoint'] == 'fanExtra':
			prender = obj['GetParameters'][0]
			dj, msg, code = self.endpoints.fanExtra(prender)
			return makeResponse(dj, msg, code)	
		elif obj['Endpoint'] == 'fanIntra':
			prender = obj['GetParameters'][0]
			dj, msg, code = self.endpoints.fanIntra(prender)
			return makeResponse(dj, msg, code)	
		elif obj['Endpoint'] == 'luz':
			prender = obj['GetParameters'][0]
			dj, msg, code = self.endpoints.luz(prender)
			return makeResponse(dj, msg, code)	
		elif obj['Endpoint'] == 'regarSegundos':
			segundos = obj['GetParameters'][0]
			dj, msg, code = self.endpoints.regarSegundos(segundos)
			return makeResponse(dj, msg, code)
		elif obj['Endpoint'] == 'cambiarEstadoProgramacion':
			idProgramacion = obj['GetParameters'][0]
			estado = obj['GetParameters'][1]
			dj, msg, code = self.endpoints.cambiarEstadoProgramacion(idProgramacion, estado)
			return makeResponse(dj, msg, code)	
		elif obj['Endpoint'] == 'borrarProgramacion':
			idProgramacion = obj['GetParameters'][0]
			dj, msg, code = self.endpoints.borrarProgramacion(idProgramacion)
			return makeResponse(dj, msg, code)
		return Respuesta(404, { 'error': 'No se encontro el endpoint solicitado' })

	def processMessage(self, message):
		with self.app.app_context():
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
		self.channel.basic_consume(self.on_request, queue=self.queueName)
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
		self.Result = str(result)
