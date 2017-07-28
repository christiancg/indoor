import modelos
import threading
import time
import traceback
import datetime

class CorredorTareas(threading.Thread):
	db = None
	segspolling = 0
	gpioluz = None
	gpiobomba = None
	gpiohumytemp = None
	gpiofanintra = None
	gpiofanextra = None
	def __init__(self,db,segspolling,gpioluz,gpiobomba,gpiohumytemp,gpiofanintra,gpiofanextra):
		threading.Thread.__init__(self)
		self.db = db
		self.segspolling = segspolling
		self.gpioluz = gpioluz
		self.gpiobomba = gpiobomba
		self.gpiohumytemp = gpiohumytemp
		self.gpiofanintra = gpiofanintra
		self.gpiofanextra = gpiofanextra
	def run(self):
		while True:
			try:
				time.sleep(self.segspolling)
				queryhorariodesde = datetime.datetime.now() - datetime.timedelta(seconds=self.segspolling)
				queryhorariohasta = datetime.datetime.now() + datetime.timedelta(seconds=self.segspolling)
				lprog = modelos.Programacion.query.filter(modelos.Programacion.habilitado==True).filter(modelos.Programacion.horario1 >= queryhorariodesde).filter(modelos.Programacion.horario1 <= queryhorariohasta).all()
				for prog in lprog:
					print 'encontro programacion para: ' + prog.configgpio.desc
					if prog.configgpio.desc == 'luz':
						if prog.prender == True:
							self.gpioluz.prenderLuz()
						else:
							self.gpioluz.apagarLuz()
					elif prog.configgpio.desc == 'bomba':
						segundos = prog.horario2 - prog.horario1
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
			except Exception,ex:
				print traceback.format_exc()
		
