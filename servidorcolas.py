import pika
import threading

class ServidorCola(threading.Thread):
	connection = None
	channel = None
	
	def __init__(self, direccion):
		threading.Thread.__init__(self)
		credentials = pika.PlainCredentials('test', 'ratablanca')
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=direccion, credentials=credentials))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue='rpc_queue')

	def fib(self,n):
		if n == 0:
			return 0
		elif n == 1:
			return 1
		else:
			return self.fib(n-1) + self.fib(n-2)

	def on_request(self, ch, method, props, body):
		n = int(body)
		print(" [.] fib(%s)" % n)
		response = self.fib(n)
		ch.basic_publish(exchange='',
						 routing_key=props.reply_to,
						 properties=pika.BasicProperties(correlation_id = props.correlation_id),
						 body=str(response))
		ch.basic_ack(delivery_tag = method.delivery_tag)

	def run(self):
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(self.on_request, queue='rpc_queue')
		print(" [x] Awaiting RPC requests")
		self.channel.start_consuming()
