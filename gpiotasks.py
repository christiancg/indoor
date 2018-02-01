import RPi.GPIO as GPIO           # import RPi.GPIO module  
import time
import pigpio
import DHT22
import modelos
from logger import Logger
log = Logger(__name__)

def updateGpioStatus(status,configgpio_id):
	try:
		toupdate = modelos.ConfigGpio.query.filter(modelos.ConfigGpio.id==configgpio_id).first()
		toupdate.estado = status
		modelos.db.session.commit()
	except Exception, ex:
		log.exception(ex)
		print traceback.format_exc()

class GpioLuz:
	GPIO_LUZ = 0

	def __init__(self,luz):
		if type(luz) is not int:
			raise TypeError('El valor del pin GPIO para la luz debe ser un entero natural')
		elif luz > 40 or luz < 1:
			raise ValueError('El valor del pin para luz no puede ser mayor a 40 ni menor a 1')
		self.GPIO_LUZ = luz
		GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
		GPIO.setup(self.GPIO_LUZ, GPIO.OUT) # set a port/pin as an output   
		GPIO.output(self.GPIO_LUZ, True)
	
	def prenderLuz(self):
		updateGpioStatus(True,self.GPIO_LUZ)
		GPIO.output(self.GPIO_LUZ, False)       # set port/pin value to 1/GPIO.HIGH/True  

	def apagarLuz(self):
		updateGpioStatus(False,self.GPIO_LUZ)
		GPIO.output(self.GPIO_LUZ, True)       # set port/pin value to 0/GPIO.LOW/False 

class GpioBomba:
	GPIO_BOMBA_AGUA = 0

	def __init__(self,bomba):
		if type(bomba) is not int:
			raise TypeError('El valor del pin GPIO para la bomba debe ser un entero natural')
		elif bomba > 40 or bomba < 1:
			raise ValueError('El valor del pin para bomba no puede ser mayor a 40 ni menor a 1')
		self.GPIO_BOMBA_AGUA = bomba
		GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
		GPIO.setup(self.GPIO_BOMBA_AGUA, GPIO.OUT) # set a port/pin as an output
		GPIO.output(self.GPIO_BOMBA_AGUA, True)

	def regarSegundos(self,segs):
		GPIO.output(self.GPIO_BOMBA_AGUA, False)
		time.sleep(float(segs))
		GPIO.output(self.GPIO_BOMBA_AGUA, True)		

class GpioFanIntra:
	GPIO_FAN_INTRA = 0

	def __init__(self,fan_intra):
		if type(fan_intra) is not int:
			raise TypeError('El valor del pin GPIO para el fan de intraccion debe ser un entero natural')
		elif fan_intra > 40 or fan_intra < 1:
			raise ValueError('El valor del pin para el fan de intraccion no puede ser mayor a 40 ni menor a 1')
		self.GPIO_FAN_INTRA = fan_intra
		GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
		GPIO.setup(self.GPIO_FAN_INTRA, GPIO.OUT) # set a port/pin as an output   
		GPIO.output(self.GPIO_FAN_INTRA, True)
		
	def prenderFanIntra(self):
		updateGpioStatus(True,self.GPIO_FAN_INTRA)
		GPIO.output(self.GPIO_FAN_INTRA, False)       # set port/pin value to 1/GPIO.HIGH/True  
	
	def apagarFanIntra(self):
		updateGpioStatus(False,self.GPIO_FAN_INTRA)
		GPIO.output(self.GPIO_FAN_INTRA, True)

class GpioFanExtra:
	GPIO_FAN_EXTRA = 0
	
	def __init__(self,fan_extra):
		if type(fan_extra) is not int:
			raise TypeError('El valor del pin GPIO para el fan de extraccion debe ser un entero natural')
		elif fan_extra > 40 or fan_extra < 1:
			raise ValueError('El valor del pin para el fan de extraccion no puede ser mayor a 40 ni menor a 1')
		self.GPIO_FAN_EXTRA = fan_extra
		GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
		GPIO.setup(self.GPIO_FAN_EXTRA, GPIO.OUT) # set a port/pin as an output   
		GPIO.output(self.GPIO_FAN_EXTRA, True)
		
	def prenderFanExtra(self):
		updateGpioStatus(True,self.GPIO_FAN_EXTRA)
		GPIO.output(self.GPIO_FAN_EXTRA, False)       # set port/pin value to 1/GPIO.HIGH/True  
		
	def apagarFanExtra(self):
		updateGpioStatus(False,self.GPIO_FAN_EXTRA)
		GPIO.output(self.GPIO_FAN_EXTRA, True)

class GpioHumYTemp:
	sensor = None
	
	def __init__(self,hum_y_temp):
		if type(hum_y_temp) is not int:
			raise TypeError('El valor del pin GPIO para el medidor de humedad y temperatura debe ser un entero natural')
		elif hum_y_temp > 40 or hum_y_temp < 1:
			raise ValueError('El valor del pin para el el medidor de humedad y temperatura no puede ser mayor a 40 ni menor a 1')
		pi = pigpio.pi()
		self.sensor = DHT22.sensor(pi,hum_y_temp)
	
	def medir(self):
		self.sensor.trigger()
		temp = self.sensor.temperature()
		hum = self.sensor.humidity()
		return temp, hum 
