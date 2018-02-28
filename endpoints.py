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
			#log.info('llego parametro sin procesar: ' + str(prender))
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
			#log.info('llego parametro procesado: ' + str(bprender))
			status = ''
			if bprender:
				#log.info('entro por prender')
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
			
	def fanIntra(self, prender):
		try:
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanintra').first()
			status = ''
			if bprender:
				status = 'Fan intracion prendido'
				self.gpiofanintra.prenderFanIntra()
			else:
				status = 'Fan intracion apagado'
				self.gpiofanintra.apagarFanIntra()		
			saveEventToDb(status, config)
			msg = json.dumps({'resultado' : status})
			return False, msg, 200
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def fanExtra(self, prender):
		try:
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanextra').first()
			status = ''
			if bprender:
				status = 'Fan extraccion prendido'
				self.gpiofanextra.prenderFanExtra()
			else:
				status = 'Fan extraccion apagado'
				self.gpiofanextra.apagarFanExtra()	
			saveEventToDb(status, config)
			msg = json.dumps({'resultado' : status})
			return False, msg, 200
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def regarSegundos(self, segs):
		try:
			desc = 'regado ' + segs + ' segundos'
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='bomba').first()
			saveEventToDb(desc, config)
			self.gpiobomba.regarSegundos(segs)
			msg = json.dumps({'resultado' : desc})
			return False, msg, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def getConfig(self):
		try:
			lconfig = modelos.ConfigGpio.query.all()
			return True, lconfig, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def humedadYTemperatura(self):
		try:
			temp, hum = self.gpiohumytemp.medir()
			devolver = { 'humedad' : hum , 'temperatura' : temp }
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='humytemp').first()
			strresponse = str(devolver)
			saveEventToDb(strresponse, config)
			msg = json.dumps(devolver)
			return False, msg, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def addProgramacion(self, dataDict):
		try:
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc==dataDict['configgpio']).first()
			if config is None:
				msg = json.dumps({'resultado': 'No se encontro la tarea a programar'})
				return False, msg, 400
				#~ return responder(json.dumps({'resultado': 'No se encontro la tarea a programar'}),400)
			desc = dataDict['desc']
			prender = dataDict['prender']
			strhorario1 = dataDict['horario1']
			horario1 = datetime.time(int(strhorario1.split(':')[0]),int(strhorario1.split(':')[1]),int(strhorario1.split(':')[2]))
			if 'horario2' in dataDict:
				strhorario2 = dataDict['horario2']
				if strhorario2:
					horario2 = datetime.time(int(strhorario2.split(':')[0]),int(strhorario2.split(':')[1]),int(strhorario2.split(':')[2]))
					if horario2 > horario1:
						nuevaProg = modelos.Programacion(desc,config,True,horario1,horario2)
					else:
						msg = json.dumps({'resultado': 'el horario2 debe ser mayor a horario1' })
						return False, msg, 400
						#~ return responder(json.dumps({'resultado': 'el horario2 debe ser mayor a horario1' }),400)
				else:
					nuevaProg = modelos.Programacion(desc,config,prender,horario1)
			else:
				nuevaProg = modelos.Programacion(desc,config,prender,horario1)
			modelos.db.session.add(nuevaProg)
			modelos.db.session.commit()
			msg = json.dumps({'resultado': 'ok' })
			return False, msg , 200
			#~ return responder(json.dumps({'resultado': 'ok' }),200)
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			#~ return responder(ex,500)
