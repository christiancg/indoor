import datetime
from flask import Flask,jsonify,request, make_response, Response
import json
import traceback
from gpiotasks import GpioLuz,GpioBomba,GpioFanIntra,GpioFanExtra,GpioHumYTemp
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/pi/Documents/proyectos/db/indoor.db'

import modelos
from modelos import db, Evento
from corredortareas import CorredorTareas

from CustomJSONEncoder import CustomJSONEncoder
encoder = CustomJSONEncoder()

#def jsonify(*args,**kwargs):
#	return app.response_class(json.dumps(dict(*args,**kwargs),cls=CustomJSONEncoder),mimetype='application/json')

def responder(obj,status):
	return Response(response=obj,status=status,mimetype='application/json') 
	
def devolverJson(obj):
	if obj is None:
		return jsonify({})
	else:
		return str(encoder.default(obj))

def saveConfigToDb(id,desc):
	try:
		toadd = modelos.ConfigGpio(id,desc)
		db.session.add(toadd)
		db.session.commit()
	except Exception, ex:
		print traceback.format_exc()
		
def saveEventToDb(desc,configgpio):
	try:
		toadd = modelos.Evento(datetime.datetime.now(),desc,configgpio)
		db.session.add(toadd)
		db.session.commit()
	except Exception, ex:
		print traceback.format_exc()

gpioluz = None
gpiobomba = None
gpiohumytemp = None
gpiofanintra = None
gpiofanextra = None

try:
	lconfig = modelos.ConfigGpio.query.all()
	for config in lconfig:
		if config.desc == 'luz':
			gpioluz = GpioLuz(config.id)
		elif config.desc == 'bomba':
			gpiobomba = GpioBomba(config.id)
		elif config.desc == 'humytemp':
			gpiohumytemp = GpioHumYTemp(config.id)
		elif config.desc == 'fanintra':
			gpiofanintra = GpioFanIntra(config.id)
		elif config.desc == 'fanextra':
			gpiofanextra = GpioFanExtra(config.id)
	if gpioluz is None:
		saveConfigToDb(13,'luz')
		gpioluz = GpioLuz(13)
	if gpiobomba is None:
		saveConfigToDb(19,'bomba')
		gpiobomba = GpioBomba(19)
	if gpiohumytemp is None:
		saveConfigToDb(4,'humytemp')
		gpiohumytemp = DHT22.sensor(pi,4)
	if gpiofanintra is None:
		saveConfigToDb(17,'fanintra')
		gpiofanintra = GpioFanIntra(17)
	if gpiofanextra is None:
		saveConfigToDb(18,'fanextra')
		gpiofanextra = GpioFanExtra(27)
except Exception, ex:
	print traceback.format_exc()
	
threadcorredor = CorredorTareas(db,10,gpioluz,gpiobomba,gpiohumytemp,gpiofanintra,gpiofanextra)
threadcorredor.start()

@app.route('/test')
def test():
    return responder("todo ok!",200)
    
@app.route('/obtenerConfiguraciones')
def getConfig():
	try:
		lconfig = modelos.ConfigGpio.query.all()
		return responder(devolverJson(lconfig),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
    
@app.route('/prenderLuz')
def prenderLuz():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
		status = 'luz prendida'
		saveEventToDb(status, config)
		gpioluz.prenderLuz()
		return responder(str({'resultado' : status}),200)
	except Exception, ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/apagarLuz')
def apagarLuz():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
		status = 'luz apagada'
		saveEventToDb(status, config)
		gpioluz.apagarLuz()
		return responder(str({'resultado' : status}),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/regarSegundos/<segs>')
def regarSegundos(segs):
	try:
		desc = 'regado ' + segs + ' segundos'
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='bomba').first()
		saveEventToDb(desc, config)
		gpiobomba.regarSegundos(segs)
		return responder(str({'resultado' : desc}),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/humedadYTemperatura')
def humedadYTemperatura():
	try:
		temp, hum = gpiohumytemp.medir()
		devolver = { 'humedad' : hum , 'temperatura' : temp }
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='humytemp').first()
		strresponse = str(devolver)
		saveEventToDb(strresponse, config)
		return responder(json.dumps(devolver),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)

@app.route('/prenderFanIntra')
def prenderFanIntra():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanintra').first()
		status = 'Fan intracion prendido'
		saveEventToDb(status, config)
		gpiofanintra.prenderFanIntra()
		return responder(str({'resultado' : status}),200)
	except Exception, ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/apagarFanIntra')
def apagarFanIntra():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanintra').first()
		status = 'Fan intracion apagado'
		saveEventToDb(status, config)
		gpiofanintra.apagarFanIntra()
		return responder(str({'resultado' : status}),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/prenderFanExtra')
def prenderFanExtra():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanextra').first()
		status = 'Fan extraccion prendido'
		saveEventToDb(status, config)
		gpiofanextra.prenderFanExtra()
		return responder(str({'resultado' : status}),200)
	except Exception, ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/apagarFanExtra')
def apagarFanExtra():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanextra').first()
		status = 'Fan extraccion apagado'
		saveEventToDb(status, config)
		gpiofanextra.apagarFanExtra()
		return responder(str({'resultado' : status}),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)


@app.route('/agregarProgramacion', methods=['POST'])
def addProgramacion():
	try:
		data = request.data
		dataDict = json.loads(data)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc==dataDict['configgpio']).first()
		if config is None:
			return 'No se encontro la tarea a programar'
		desc = dataDict['desc']
		prender = dataDict['prender']
		strhorario1 = dataDict['horario1']
		horario1 = datetime.time(int(strhorario1.split(':')[0]),int(strhorario1.split(':')[1]),int(strhorario1.split(':')[2]))
		if 'horario2' in dataDict:
			strhorario2 = dataDict['horario2']
			horario2 = datetime.time(int(strhorario2.split(':')[0]),int(strhorario2.split(':')[1]),int(strhorario2.split(':')[2]))
			if horario2 > horario1:
				nuevaProg = modelos.Programacion(desc,config,True,horario1,horario2)
			else:
				return 'el horario2 debe ser mayor a horario1'
		else:
			nuevaProg = modelos.Programacion(desc,config,prender,horario1)
		db.session.add(nuevaProg)
		db.session.commit()
		return responder(json.dumps({'resultado': 'ok' }),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)

@app.route('/obtenerProgramaciones')
def obtenerProgramaciones():
	try:
		lprog = modelos.Programacion.query.filter(modelos.Programacion.habilitado==True).all()
		return responder(devolverJson(lprog),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/obtenerEventosPorFecha/<fechaInicio>/<fechaFin>')
@app.route('/obtenerEventosPorFecha/<fechaInicio>/<fechaFin>/<tipoEvento>')
def obtenerEventosPorFecha(fechaInicio,fechaFin,tipoEvento=''):
	try:
		inicio = None
		fin = None
		try:
			inicio = datetime.datetime.strptime(fechaInicio, '%d-%m-%YT%H:%M:%S') 
			fin = datetime.datetime.strptime(fechaFin, '%d-%m-%YT%H:%M:%S')
		except Exception:
			print traceback.format_exc()
			error = { 'error' : 'Tanto la fecha de inicio y la fecha de fin deben ser fechas con formato dd-MM-yyyyThh:mm:ss' }
			return make_response(jsonify(error),400)
		if inicio > fin:
			error = { 'error' : 'La fecha de inicio no puede ser inferior a la fecha de fin' }
			return make_response(jsonify(error),400)
		leventos = None
		if tipoEvento == '':
			leventos = modelos.Evento.query.filter(modelos.Evento.fechayhora > inicio).filter(modelos.Evento.fechayhora < fin).all()
		else:
			leventos = modelos.Evento.query.filter(modelos.Evento.fechayhora > inicio).filter(modelos.Evento.fechayhora < fin).join(modelos.Evento.configgpio).filter(modelos.ConfigGpio.desc == tipoEvento).all()
		if leventos is None:
			return make_response(jsonify([]),200)
		else:
			return responder(devolverJson(leventos),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=9090)
