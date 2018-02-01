import pika
import threading
import traceback
import jsonpickle
from logger import Logger
log = Logger(__name__)

class ServidorCola(threading.Thread):
	connection = None
	channel = None
	
	def __init__(self, direccion):
		threading.Thread.__init__(self)
		credentials = pika.PlainCredentials('test', 'ratablanca')
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=direccion, credentials=credentials))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue='rpc_queue')

	def processMessage(self, message):
		print(str(message))
		try:
			return jsonpickle.encode(Respuesta(200, True, "Test OK", {}))
		except Exception, ex:
			log.exception(ex)
			return jsonpickle.encode(Respuesta(500, False, "Error generalizado", ex))
			print traceback.format_exc()

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
	Message = ""
	Result = {}
	def __init__(self, statusCode, success, message, result):
		self.StatusCode = statusCode
		self.Success = success
		self.Message = message
		self.Result = result
