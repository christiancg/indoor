import logging
import configuration

class Logger(object):
	basiclogger = None

	def __init__(self, name):
		self.basiclogger = logging.getLogger(name)
		hdlr = logging.FileHandler(configuration.loggerRoute)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -> %(message)s')
		hdlr.setFormatter(formatter)
		self.basiclogger.addHandler(hdlr) 
		self.basiclogger.setLevel(logging.DEBUG)
	
	def info(self, message):
		self.basiclogger.info(message)
	
	def error(self, message):
		self.basiclogger.error(message)
		
	def warning(self, message):
		self.basiclogger.warning(message)
		
	def debug(self, message):
		self.basiclogger.debug(message)
		
	def critical(self, message):
		self.basiclogger.critical(message)
		
	def exception(self, ex):
		self.basiclogger.exception(ex)
