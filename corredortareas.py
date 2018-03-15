import modelos
import threading
import time
import traceback
import datetime
from logger import Logger

class CorredorTareas(threading.Thread):
	app = None
	db = None
	segspolling = 0
	gpioluz = None
	gpiobomba = None
	gpiohumytemp = None
	gpiofanintra = None
	gpiofanextra = None
	log = None
	def __init__(self,app,db,segspolling,gpioluz,gpiobomba,gpiohumytemp,gpiofanintra,gpiofanextra):
		threading.Thread.__init__(self)
		self.app = app
		self.db = db
		self.segspolling = segspolling
		self.gpioluz = gpioluz
		self.gpiobomba = gpiobomba
		self.gpiohumytemp = gpiohumytemp
		self.gpiofanintra = gpiofanintra
		self.gpiofanextra = gpiofanextra
		self.log = Logger(__name__)
	def run(self):
		with self.app.app_context():
			while True:
				try:
					time.sleep(self.segspolling)
					queryhorariodesde = datetime.datetime.now().time()
					queryhorariohasta = datetime.datetime.now() + datetime.timedelta(seconds=self.segspolling)
					queryhorariohasta = queryhorariohasta.time()
					lprog = modelos.Programacion.query.filter(modelos.Programacion.habilitado==True).filter(modelos.Programacion.horario1 >= queryhorariodesde).filter(modelos.Programacion.horario1 <= queryhorariohasta).all()
					for prog in lprog:
						print 'encontro programacion para: ' + prog.configgpio.desc
						if prog.configgpio.desc == 'luz':
							if prog.prender == True:
								self.gpioluz.prenderLuz()
							else:
								self.gpioluz.apagarLuz()
						elif prog.configgpio.desc == 'bomba':
							segundos = prog.duracion
							intsegs = int(segundos)
							self.gpiobomba.regarSegundos(intsegs)
						elif prog.configgpio.desc == 'humytemp':
							self.gpiohumytemp.medir()
						elif prog.configgpio.desc == 'fanintra':
							if prog.prender == True:
								self.gpiofanintra.prenderFanIntra()
							else:
								self.gpiofanintra.apagarFanIntra()
						elif prog.configgpio.desc == 'fanextra':
							if prog.prender == True:
								self.gpiofanextra.prenderFanExtra()
							else:
								self.gpiofanextra.apagarFanExtra()
						self.saveEventToDb(prog)
				except Exception,ex:
					self.log.exception(ex)
					print traceback.format_exc()
		
	def saveEventToDb(self,prog):
		try:
			descripcion_evento = 'Se ejecuto programacion: ' + prog.desc
			toadd = modelos.Evento(datetime.datetime.now(),descripcion_evento,prog.configgpio)
			self.db.session.add(toadd)
			self.db.session.commit()
		except Exception, ex:
			self.log.exception(ex)
			print traceback.format_exc()
