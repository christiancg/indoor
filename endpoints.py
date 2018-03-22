import traceback
import datetime
import json
from distutils import util
from camara import Camara

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
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
			if config is not None:
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
			else:
				msg = json.dumps({'resultado' : 'esta funcionalidad no se encuentra habilitada'})
				return False, msg, 400
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def fanIntra(self, prender):
		try:
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanintra').first()
			if config is not None:
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
			else:
				msg = json.dumps({'resultado' : 'esta funcionalidad no se encuentra habilitada'})
				return False, msg, 400
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def fanExtra(self, prender):
		try:
			bprender = util.strtobool(prender)
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanextra').first()
			if config is not None:
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
			else:
				msg = json.dumps({'resultado' : 'esta funcionalidad no se encuentra habilitada'})
				return False, msg, 400
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def regarSegundos(self, segs):
		try:
			desc = 'regado ' + segs + ' segundos'
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='bomba').first()
			if config is not None:
				saveEventToDb(desc, config)
				self.gpiobomba.regarSegundos(segs)
				msg = json.dumps({'resultado' : desc})
				return False, msg, 200
			else:
				msg = json.dumps({'resultado' : 'esta funcionalidad no se encuentra habilitada'})
				return False, msg, 400
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
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='humytemp').first()
			if config is not None:
				temp, hum = self.gpiohumytemp.medir()
				devolver = { 'humedad' : hum , 'temperatura' : temp }
				strresponse = str(devolver)
				saveEventToDb(strresponse, config)
				msg = json.dumps(devolver)
				return False, msg, 200
			else:
				msg = json.dumps({'resultado' : 'esta funcionalidad no se encuentra habilitada'})
				return False, msg, 400
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
			desc = dataDict['desc']
			prender = dataDict['prender']
			strhorario1 = dataDict['horario1']
			horario1 = datetime.time(int(strhorario1.split(':')[0]),int(strhorario1.split(':')[1]),int(strhorario1.split(':')[2]))
			if 'duracion' in dataDict:
				strduracion = dataDict['duracion']
				if strduracion:
					duracion = int(strduracion)
					if duracion > 0:
						nuevaProg = modelos.Programacion(desc,config,True,horario1,duracion)
					else:
						msg = json.dumps({'resultado': 'La duracion debe ser mayor a 0' })
						return False, msg, 400
				else:
					nuevaProg = modelos.Programacion(desc,config,prender,horario1)
			else:
				nuevaProg = modelos.Programacion(desc,config,prender,horario1)
			modelos.db.session.add(nuevaProg)
			modelos.db.session.commit()
			msg = json.dumps({'resultado': 'ok' })
			return False, msg , 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
	
	def editarProgramacion(self, dataDict):		
		try:
			prog = modelos.Programacion.query.filter(modelos.Programacion.id==dataDict['id']).first()
			if prog is None:
				msg = json.dumps({'resultado': 'No se encontro la programacion a editar'})
				return False, msg, 400
			config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc==dataDict['configgpio']).first()
			if config is None:
				msg = json.dumps({'resultado': 'No se encontro la configgpio deseada para editar'})
				return False, msg, 400
			desc = dataDict['desc']
			prender = dataDict['prender']
			strhorario1 = dataDict['horario1']
			horario1 = datetime.time(int(strhorario1.split(':')[0]),int(strhorario1.split(':')[1]),int(strhorario1.split(':')[2]))
			if 'duracion' in dataDict:
				strduracion = dataDict['duracion']
				if strduracion:
					duracion = int(strduracion)
					if duracion > 0:
						prog.configgpio = config
						prog.desc = desc
						prog.prender = prender
						prog.horario1 = horario1
						prog.duracion = duracion
					else:
						msg = json.dumps({'resultado': 'La duracion debe ser mayor a 0' })
						return False, msg, 400
				else:
						prog.configgpio = config
						prog.desc = desc
						prog.prender = prender
						prog.horario1 = horario1
			else:
				prog.configgpio = config
				prog.desc = desc
				prog.prender = prender
				prog.horario1 = horario1
			modelos.db.session.merge(prog)
			modelos.db.session.commit()
			msg = json.dumps({'resultado': 'ok' })
			return False, msg, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def cambiarEstadoProgramacion(self, id, estado):
		try:
			try:
				estado = util.strtobool(estado)
			except Exception, exp:
				log.exception(exp)
				msg = json.dumps({'resultado': 'El parametro estado debe ser true o false'})
				return False, msg, 400
			prog = modelos.Programacion.query.filter(modelos.Programacion.id==id).first()
			if prog is None:
				msg = json.dumps({'resultado': 'No se encontro la programacion a cambiar estado'})
				return False, msg, 400
			prog.habilitado = estado
			modelos.db.session.merge(prog)
			modelos.db.session.commit()
			msg = json.dumps({'resultado': 'estado de programacion cambiado' })
			return False, msg, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def borrarProgramacion(self, id):
		try:
			prog = modelos.Programacion.query.filter(modelos.Programacion.id==id).first()
			if prog is None:
				msg = json.dumps({'resultado': 'No se encontro la programacion a borrar'})
				return False, msg, 400
			modelos.db.session.delete(prog)
			modelos.db.session.commit()
			msg = json.dumps({'resultado': 'programacion borrada' })
			return False, msg, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def obtenerProgramaciones(self):
		try:
			lprog = modelos.Programacion.query.all()
			return True, lprog, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
				
	def obtenerEventosPorFecha(self, fechaInicio,fechaFin,tipoEvento=''):
		try:
			inicio = None
			fin = None
			try:
				inicio = datetime.datetime.strptime(fechaInicio, '%d-%m-%YT%H:%M:%S') 
				fin = datetime.datetime.strptime(fechaFin, '%d-%m-%YT%H:%M:%S')
			except Exception, exp:
				log.exception(exp)
				print traceback.format_exc()
				error = json.dumps({ 'error' : 'Tanto la fecha de inicio y la fecha de fin deben ser fechas con formato dd-MM-yyyyThh:mm:ss' })
				return False, error, 400
			if inicio > fin:
				error = json.dumps({ 'error' : 'La fecha de inicio no puede ser inferior a la fecha de fin' })
				return False, error, 400
			leventos = None
			if tipoEvento == '':
				leventos = modelos.Evento.query.filter(modelos.Evento.fechayhora > inicio).filter(modelos.Evento.fechayhora < fin).all()
			else:
				leventos = modelos.Evento.query.filter(modelos.Evento.fechayhora > inicio).filter(modelos.Evento.fechayhora < fin).join(modelos.Evento.configgpio).filter(modelos.ConfigGpio.desc == tipoEvento).all()
			if leventos is None:
				msg = json.dumps([])
				return False, msg, 200
			else:
				return True, leventos, 200
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
			
	def obtenerImagenIndoor(self):
		try:
			result = {}
			with Camara(30) as cam:
				tomo, imagen = cam.obtenerImagen()
				result['status'] = tomo
				if tomo:
					date = str(datetime.datetime.now())
					result = { 'status':tomo, 'b64image': imagen, 'date': date }
				else:
					result = { 'status':tomo, 'msg': imagen }
			msg = json.dumps(result)
			if result['status']:
				return False, msg, 200
			else:
				return False, msg, 500
		except Exception,ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, ex, 500
