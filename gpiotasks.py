import RPi.GPIO as GPIO           # import RPi.GPIO module  
import time

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
		GPIO.output(self.GPIO_LUZ, False)       # set port/pin value to 1/GPIO.HIGH/True  

	def apagarLuz(self):
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
	
	def prenderFanIntra():
		GPIO.output(self.GPIO_FAN_INTRA, False)       # set port/pin value to 1/GPIO.HIGH/True  
	
	def apagarFanIntra():
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
	
	def prenderFanExtra():
		GPIO.output(self.GPIO_FAN_EXTRA, False)       # set port/pin value to 1/GPIO.HIGH/True  
		
	def apagarFanExtra():
		GPIO.output(self.GPIO_FAN_EXTRA, True)
