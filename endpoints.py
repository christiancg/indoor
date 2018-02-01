import traceback
import datetime
import json
from distutils import util

import modelos
from logger import Logger
log = Logger(__name__)


def saveEventToDb(desc,configgpio):
    try:
		toadd = modelos.Evento(datetime.datetime.now(),desc,configgpio)
		modelos.db.session.add(toadd)
		modelos.db.session.commit()
    except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()
		
class Endpoints(object):
	gpioluz = None
	gpiobomba = None
	gpiohumytemp = None
	gpiofanintra = None
	gpiofanextra = None

	def __init__(self, luz, bomba, humytemp, fanintra, fanextra):
		self.gpioluz = luz
		self.gpiobomba = bomba
		self.gpiohumytemp = humytemp
		self.gpiofanintra = fanintra
		self.gpiofanextra = fanextra
		
	# LOS METODOS SIEMPRE DEVUELVEN 3 COSAS: 1-> DEVOLVERJSON(TRUE/FALSE), 2-> MENSAJE, 3-> STATUS CODE (INT)
	
	def luz(self, prender):
		try:
			log.info('llego parametro sin procesar: ' + str(prender))
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
			log.info('llego parametro procesado: ' + str(bprender))
			status = ''
			if bprender:
				log.info('entro por prender')
				status = 'luz prendida'
				self.gpioluz.prenderLuz()
			else:
				status = 'luz apagada'
				self.gpioluz.apagarLuz()
			saveEventToDb(status, config)
			msg = json.dumps({'resultado' : status})
			return False, msg, 200
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
