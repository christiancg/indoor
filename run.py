import datetime
from flask import Flask,jsonify,request, make_response
import json
import traceback
from gpiotasks import GpioLuz,GpioBomba,GpioFanIntra,GpioFanExtra
from sqlalchemy.orm import joinedload
import pigpio
pi = pigpio.pi()
import DHT22

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/pi/Documents/proyectos/db/indoor.db'

import modelos
from modelos import db

from CustomJSONEncoder import CustomJSONEncoder
encoder = CustomJSONEncoder()

#def jsonify(*args,**kwargs):
#	return app.response_class(json.dumps(dict(*args,**kwargs),cls=CustomJSONEncoder),mimetype='application/json')
	
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
			gpiohumytemp = DHT22.sensor(pi,config.id)
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
		saveConfigToDb(27,'fanextra')
		gpiofanextra = GpioFanExtra(27)
except Exception, ex:
	print traceback.format_exc()
	


@app.route('/test')
def hello():
    return "todo ok!"
    
@app.route('/obtenerConfiguraciones')
def getConfig():
	try:
		lconfig = modelos.ConfigGpio.query.all()
		return devolverJson(lconfig)
	except Exception,ex:
		print traceback.format_exc()
		return jsonify(ex)
    
@app.route('/prenderLuz')
def prenderLuz():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
		saveEventToDb('luz prendida', config)
		gpioluz.prenderLuz()
		return 'luz prendida'
	except Exception, ex:
		print traceback.format_exc()
		return ex
		
@app.route('/apagarLuz')
def apagarLuz():
	try:
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
		saveEventToDb('luz apagada', config)
		gpioluz.apagarLuz()
		return 'luz apagada'
	except Exception,ex:
		print traceback.format_exc()
		return ex
		
@app.route('/regarSegundos/<segs>')
def regarSegundos(segs):
	try:
		desc = 'regado ' + segs + ' segundos'
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='bomba').first()
		saveEventToDb(desc, config)
		gpiobomba.regarSegundos(segs)
		return desc
	except Exception,ex:
		print traceback.format_exc()
		return ex
		
@app.route('/humedadYTemperatura')
def humedadYTemperatura():
	try:
		gpiohumytemp.trigger()
		temp = gpiohumytemp.temperature()
		hum = gpiohumytemp.humidity()
		devolver = { 'humedad' : hum , 'temperatura' : temp }
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='humytemp').first()
		saveEventToDb(str(devolver), config)
		return jsonify(devolver)
	except Exception,ex:
		print traceback.format_exc()
		return ex


@app.route('/agregarProgramacion', methods=['POST'])
def addProgramacion():
	try:
		data = request.data
		dataDict = json.loads(data)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc==dataDict['configgpio']).first()
		if config is None:
			return 'No se encontro la tarea a programar'
		desc = dataDict['desc']
		strhorario1 = dataDict['horario1']
		horario1 = datetime.time(int(strhorario1.split(':')[0]),int(strhorario1.split(':')[1]),int(strhorario1.split(':')[2]))
		if 'horario2' in dataDict:
			strhorario2 = dataDict['horario2']
			horario2 = datetime.time(int(strhorario2.split(':')[0]),int(strhorario2.split(':')[1]),int(strhorario2.split(':')[2]))
			if horario2 > horario1:
				nuevaProg = modelos.Programacion(desc,config,horario1,horario2)
			else:
				return 'el horario2 debe ser mayor a horario1'
		else:
			nuevaProg = modelos.Programacion(desc,config,horario1)
		db.session.add(nuevaProg)
		db.session.commit()
		return 'ok'
	except Exception,ex:
		print traceback.format_exc()
		return ex

@app.route('/obtenerProgramaciones')
def obtenerProgramaciones():
	try:
		lprog = modelos.Programacion.query.filter(modelos.Programacion.habilitado==True).all()
		return devolverJson(lprog)
	except Exception,ex:
		print traceback.format_exc()
		return ex
		
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
			return jsonify(error)
		leventos = None
		if tipoEvento == '':
			leventos = modelos.Evento.query.filter(modelos.Evento.fechayhora > fechaInicio).filter(modelos.Evento.fechayhora > fechaFin).all()
		else:
			#leventos = modelos.Evento.query.filter(modelos.Evento.fechayhora > fechaInicio).filter(modelos.Evento.fechayhora < fechaFin).join(modelos.ConfigGpio,modelos.Evento.configgpio).filter(modelos.ConfigGpio.desc == tipoEvento).all()
			leventos = db.session.query(modelos.Evento).filter(modelos.Evento.fechayhora > fechaInicio).filter(modelos.Evento.fechayhora < fechaFin).join(modelos.Evento.configgpio).filter(modelos.ConfigGpio.desc == tipoEvento).all()
		if leventos is None:
			return jsonify([])
		else:
			return devolverJson(leventos)
	except Exception,ex:
		print traceback.format_exc()
		return ex
		
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=9090)
