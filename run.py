import datetime
from flask import Flask,jsonify,request, make_response, Response
import json
import traceback
import time
import gpiotasks
from sqlalchemy.orm import joinedload
import distutils
from distutils import util

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/pi/Documents/proyectos/db/indoor.db'

import modelos
from corredortareas import CorredorTareas

from camara import Camara

from CustomJSONEncoder import CustomJSONEncoder
encoder = CustomJSONEncoder()

#def jsonify(*args,**kwargs):
#	return app.response_class(json.dumps(dict(*args,**kwargs),cls=CustomJSONEncoder),mimetype='application/json')

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
		print traceback.format_exc()
		
def saveEventToDb(desc,configgpio):
	try:
		toadd = modelos.Evento(datetime.datetime.now(),desc,configgpio)
		modelos.db.session.add(toadd)
		modelos.db.session.commit()
	except Exception, ex:
		print traceback.format_exc()

gpioluz = None
gpiobomba = None
gpiohumytemp = None
gpiofanintra = None
gpiofanextra = None

with app.app_context():
	modelos.db.init_app(app)
	modelos.db.create_all()
	#primero configuracion de las interfaces fisicas
	try:
		lconfig = modelos.ConfigGpio.query.all()
		for config in lconfig:
			if config.desc == 'luz':
				gpioluz = gpiotasks.GpioLuz(config.id)
				if config.estado:
					time.sleep(5)
					gpioluz.prenderLuz()
			elif config.desc == 'bomba':
				gpiobomba = gpiotasks.GpioBomba(config.id)
			elif config.desc == 'humytemp':
				gpiohumytemp = gpiotasks.GpioHumYTemp(config.id)
			elif config.desc == 'fanintra':
				gpiofanintra = gpiotasks.GpioFanIntra(config.id)
				if config.estado:
					time.sleep(5)
					gpiofanintra.prenderFanIntra()
			elif config.desc == 'fanextra':
				gpiofanextra = gpiotasks.GpioFanExtra(config.id)
				if config.estado:
					time.sleep(5)
					gpiofanextra.prenderFanExtra()
		if gpioluz is None:
			saveConfigToDb(13,'luz')
			gpioluz = gpiotasks.GpioLuz(13)
		if gpiobomba is None:
			saveConfigToDb(19,'bomba')
			gpiobomba = gpiotasks.GpioBomba(19)
		if gpiohumytemp is None:
			saveConfigToDb(4,'humytemp')
			gpiohumytemp = gpiotasks.GpioHumYTemp(4)
		if gpiofanintra is None:
			saveConfigToDb(17,'fanintra')
			gpiofanintra = gpiotasks.GpioFanIntra(17)
		if gpiofanextra is None:
			saveConfigToDb(18,'fanextra')
			gpiofanextra = gpiotasks.GpioFanExtra(27)
	except Exception, ex:
		print traceback.format_exc()
	#lueg configuracion del corredor de tareas
	try:
		threadcorredor = CorredorTareas(app,modelos.db,10,gpioluz,gpiobomba,gpiohumytemp,gpiofanintra,gpiofanextra)
		threadcorredor.start()
	except Exception, ex:
		print traceback.format_exc()

@app.route('/test')
def test():
    return responder("todo ok!",200)
    
@app.route('/obtenerConfiguraciones')
def getConfig():
	try:
		lconfig = modelos.ConfigGpio.query.all()
		return devolverJson(lconfig,200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/luz/<prender>')
def luz(prender):
	try:
		bprender = util.strtobool(prender)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='luz').first()
		status = ''
		if bprender:
			status = 'luz prendida'
			gpioluz.prenderLuz()
		else:
			status = 'luz apagada'
			gpioluz.apagarLuz()
		saveEventToDb(status, config)
		return responder(json.dumps({'resultado' : status}),200)
	except Exception, ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/regarSegundos/<segs>')
def regarSegundos(segs):
	try:
		desc = 'regado ' + segs + ' segundos'
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='bomba').first()
		saveEventToDb(desc, config)
		gpiobomba.regarSegundos(segs)
		return responder(json.dumps({'resultado' : desc}),200)
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
		
@app.route('/fanIntra/<prender>')
def fanIntra(prender):
	try:
		bprender = util.strtobool(prender)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanintra').first()
		status = ''
		if bprender:
			status = 'Fan intracion prendido'
			gpiofanintra.prenderFanIntra()
		else:
			status = 'Fan intracion apagado'
			gpiofanintra.apagarFanIntra()		
		saveEventToDb(status, config)
		return responder(json.dumps({'resultado' : status}),200)
	except Exception, ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/fanExtra/<prender>')
def fanExtra(prender):
	try:
		bprender = util.strtobool(prender)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc=='fanextra').first()
		status = ''
		if bprender:
			status = 'Fan extraccion prendido'
			gpiofanextra.prenderFanExtra()
		else:
			status = 'Fan extraccion apagado'
			gpiofanextra.apagarFanExtra()	
		saveEventToDb(status, config)
		return responder(json.dumps({'resultado' : status}),200)
	except Exception, ex:
		print traceback.format_exc()
		return responder(ex,500)

@app.route('/agregarProgramacion', methods=['POST'])
def addProgramacion():
	try:
		data = request.data
		dataDict = json.loads(data)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc==dataDict['configgpio']).first()
		if config is None:
			return responder(json.dumps({'resultado': 'No se encontro la tarea a programar'}),400)
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
					return responder(json.dumps({'resultado': 'el horario2 debe ser mayor a horario1' }),400)
			else:
				nuevaProg = modelos.Programacion(desc,config,prender,horario1)
		else:
			nuevaProg = modelos.Programacion(desc,config,prender,horario1)
		modelos.db.session.add(nuevaProg)
		modelos.db.session.commit()
		return responder(json.dumps({'resultado': 'ok' }),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/editarProgramacion', methods=['PUT'])
def editarProgramacion():
	try:
		data = request.data
		dataDict = json.loads(data)
		prog = modelos.Programacion.query.filter(modelos.Programacion.id==dataDict['id']).first()
		if prog is None:
			return responder(json.dumps({'resultado': 'No se encontro la programacion a editar'}),400)
		config = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.desc==dataDict['configgpio']).first()
		if config is None:
			return responder(json.dumps({'resultado': 'No se encontro la configgpio deseada para editar'}),400)
		desc = dataDict['desc']
		prender = dataDict['prender']
		strhorario1 = dataDict['horario1']
		horario1 = datetime.time(int(strhorario1.split(':')[0]),int(strhorario1.split(':')[1]),int(strhorario1.split(':')[2]))
		if 'horario2' in dataDict:
			strhorario2 = dataDict['horario2']
			if strhorario2:
				horario2 = datetime.time(int(strhorario2.split(':')[0]),int(strhorario2.split(':')[1]),int(strhorario2.split(':')[2]))
				if horario2 > horario1:
					prog.configgpio = config
					prog.desc = desc
					prog.prender = prender
					prog.horario1 = horario1
					prog.horario2 = horario2
				else:
					return responder(json.dumps({'resultado': 'el horario2 debe ser mayor a horario1' }),400)
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
		return responder(json.dumps({'resultado': 'ok' }),200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)

@app.route('/obtenerProgramaciones')
def obtenerProgramaciones():
	try:
		lprog = modelos.Programacion.query.filter(modelos.Programacion.habilitado==True).all()
		return devolverJson(lprog,200)
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
			return devolverJson(leventos,200)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
@app.route('/obtenerImagenIndoor')
def obtenerImagenIndoor():
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
		if result['status']:
			return responder(json.dumps(result),200)
		else:
			return responder(json.dumps(result),500)
	except Exception,ex:
		print traceback.format_exc()
		return responder(ex,500)
		
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=9090)
