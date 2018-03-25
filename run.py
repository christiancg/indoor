import datetime
from flask import Flask,jsonify,request, make_response, Response
import json
import traceback
import time
import gpiotasks
from sqlalchemy.orm import joinedload

from logger import Logger
log = Logger(__name__)
log.info('app iniciando')

import configuration 

from os.path import expanduser
home = expanduser("~")
file_path = home + "/indoor-config/db/indoor.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path

log.info('La base de datos esta en: ' + app.config['SQLALCHEMY_DATABASE_URI'])

import modelos
from corredortareas import CorredorTareas

from CustomJSONEncoder import CustomJSONEncoder
encoder = CustomJSONEncoder()

import servidorcolas

from authenticationdecorator import requires_auth

def responder(obj,status):
	return Response(response=obj,status=status,mimetype='application/json') 
	
def devolverJson(obj,status):
	if obj is None:
		return responder(jsonify({}),status)
	else:
		devolver = json.dumps(encoder.default(obj))
		return responder(devolver,status)

def saveConfigToDb(id,desc):
	try:
		toadd = modelos.ConfigGpio(id,desc)
		modelos.db.session.add(toadd)
		modelos.db.session.commit()
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()
		
def deleteConfigFromDb(todelete):
	try:
		modelos.db.session.delete(todelete)
		modelos.db.session.commit()
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()
		
def saveEventToDb(desc,configgpio):
	try:
		toadd = modelos.Evento(datetime.datetime.now(),desc,configgpio)
		modelos.db.session.add(toadd)
		modelos.db.session.commit()
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()

gpioluz = None
gpiobomba = None
gpiohumytemp = None
gpiofanintra = None
gpiofanextra = None
camara = None

from endpoints import Endpoints
ep = None

with app.app_context():
	modelos.db.init_app(app)
	modelos.db.create_all()
	#primero configuracion de las interfaces fisicas
	try:
		dbluz = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
		if configuration.tiene_luz:
			gpioluz = gpiotasks.GpioLuz(13)
			if dbluz is None:
				saveConfigToDb(13,'luz')
			elif dbluz.estado:
				time.sleep(5)
				gpioluz.prenderLuz()
		else:
			if dbluz is not None:
				deleteConfigFromDb(dbluz)
		dbbomba = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='bomba').first()
		if configuration.tiene_bomba:
			gpiobomba = gpiotasks.GpioBomba(19)
			if dbbomba is None:
				saveConfigToDb(19,'bomba')
		else:
			if dbbomba is not None:
				deleteConfigFromDb(dbbomba)
		dbhumytemp = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='humytemp').first()
		if configuration.tiene_humytemp:
			gpiohumytemp = gpiotasks.GpioHumYTemp(4)
			if dbhumytemp is None:
				saveConfigToDb(4,'humytemp')
		else:
			if dbhumytemp is not None:
				deleteConfigFromDb(dbhumytemp)
		dbfanintra = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanintra').first()
		if configuration.tiene_fanintra:
			gpiofanintra = gpiotasks.GpioFanIntra(17)
			if dbfanintra is None:
				saveConfigToDb(17,'fanintra')
			elif dbfanintra.estado:
				time.sleep(5)
				gpiofanintra.prenderFanIntra()
		else:
			if dbfanintra is not None:
				deleteConfigFromDb(dbfanintra)
		dbfanextra = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanextra').first()
		if configuration.tiene_fanextra:
			gpiofanextra = gpiotasks.GpioFanExtra(18)
			if dbfanextra is None:
				saveConfigToDb(18,'fanextra')
			elif dbfanextra.estado:
				time.sleep(5)
				gpiofanextra.prenderFanExtra()
		else:
			if dbfanextra is not None:
				deleteConfigFromDb(dbfanextra)
		dbcamara = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='camara').first()
		if configuration.tiene_camara:
			if dbcamara is None:
				saveConfigToDb(99,'camara')
		else:
			if dbcamara is not None:
				deleteConfigFromDb(dbcamara)
			
		#~ lconfig = modelos.ConfigGpio.query.all()
		#~ for config in lconfig:
			#~ if config.desc == 'luz':
				#~ gpioluz = gpiotasks.GpioLuz(config.id)
				#~ if config.estado:
					#~ time.sleep(5)
					#~ gpioluz.prenderLuz()
			#~ elif config.desc == 'fanintra':
				#~ gpiofanintra = gpiotasks.GpioFanIntra(config.id)
				#~ if config.estado:
					#~ time.sleep(5)
					#~ gpiofanintra.prenderFanIntra()
			#~ elif config.desc == 'fanextra':
				#~ gpiofanextra = gpiotasks.GpioFanExtra(config.id)
				#~ if config.estado:
					#~ time.sleep(5)
					#~ gpiofanextra.prenderFanExtra()
					
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()
	#creacion de objeto que contiene los endpoints
	ep = Endpoints(gpioluz, gpiobomba, gpiohumytemp, gpiofanintra, gpiofanextra)
	#lueg configuracion del corredor de tareas
	try:
		threadcorredor = CorredorTareas(app,modelos.db,10,gpioluz,gpiobomba,gpiohumytemp,gpiofanintra,gpiofanextra)
		threadcorredor.start()
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()
	try:
		cola = servidorcolas.ServidorCola(configuration.queueUrl, configuration.queueName, configuration.queueUser, configuration.queuePassword, app, ep)
		cola.start()
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()

def finalizarRespuesta(dj, msg, code):
	if dj:
		return devolverJson(msg,code)
	else:
		return responder(msg,code)

@app.route('/test')
@requires_auth
def test():
    return responder("todo ok!",200)
    
@app.route('/obtenerConfiguraciones')
@requires_auth
def getConfig():
	dj, msg, code = ep.getConfig()
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/luz/<prender>')
@requires_auth
def luz(prender):
	dj, msg, code = ep.luz(prender)
	return finalizarRespuesta(dj, msg, code)

@app.route('/fanIntra/<prender>')
@requires_auth
def fanIntra(prender):
	dj, msg, code = ep.fanIntra(prender)
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/fanExtra/<prender>')
@requires_auth
def fanExtra(prender):
	dj, msg, code = ep.fanExtra(prender)
	return finalizarRespuesta(dj, msg, code)
			
@app.route('/regarSegundos/<segs>')
@requires_auth
def regarSegundos(segs):
	dj, msg, code = ep.regarSegundos(segs)
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/humedadYTemperatura')
@requires_auth
def humedadYTemperatura():
	dj, msg, code = ep.humedadYTemperatura()
	return finalizarRespuesta(dj, msg, code)

@app.route('/agregarProgramacion', methods=['POST'])
@requires_auth
def addProgramacion():
	data = request.data
	dataDict = json.loads(data)
	dj, msg, code = ep.addProgramacion(dataDict)
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/editarProgramacion', methods=['PUT'])
@requires_auth
def editarProgramacion():
	data = request.data
	dataDict = json.loads(data)
	dj, msg, code = ep.editarProgramacion(dataDict)
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/cambiarEstadoProgramacion/<id>/<estado>', methods=['PUT'])
@requires_auth
def cambiarEstadoProgramacion(id, estado):
	dj, msg, code = ep.cambiarEstadoProgramacion(id, estado)
	return finalizarRespuesta(dj, msg, code)
	
@app.route('/borrarProgramacion/<id>', methods=['DELETE'])
@requires_auth
def borrarProgramacion(id):
	dj, msg, code = ep.borrarProgramacion(id)
	return finalizarRespuesta(dj, msg, code)

@app.route('/obtenerProgramaciones')
@requires_auth
def obtenerProgramaciones():
	dj, msg, code = ep.obtenerProgramaciones()
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/obtenerEventosPorFecha/<fechaInicio>/<fechaFin>')
@app.route('/obtenerEventosPorFecha/<fechaInicio>/<fechaFin>/<tipoEvento>')
@requires_auth
def obtenerEventosPorFecha(fechaInicio,fechaFin,tipoEvento=''):
	dj, msg, code = ep.obtenerEventosPorFecha(fechaInicio,fechaFin,tipoEvento)
	return finalizarRespuesta(dj, msg, code)
		
@app.route('/obtenerImagenIndoor')
@requires_auth
def obtenerImagenIndoor():
	dj, msg, code = ep.obtenerImagenIndoor()
	return finalizarRespuesta(dj, msg, code)
		
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=9090)
