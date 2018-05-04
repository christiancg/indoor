#~ import cv2
#~ import base64

#~ class Camara(object):
	#~ FRAMES_CALIBRACION = 0
	#~ CAMARA = None
	
	#~ def __init__(self, framescalibracion):
		#~ self.FRAMES_CALIBRACION = framescalibracion
		#~ self.CAMARA = cv2.VideoCapture(0)
		#~ if not self.CAMARA.isOpened():
			#~ self.CAMARA.release()
			#~ self.CAMARA = cv2.VideoCapture(-1)
	
	#~ def __enter__(self):
		#~ return self
		
	#~ def __exit__(self, exc_type, exc_value, traceback):
		#~ self.CAMARA.release()
		#~ cv2.destroyAllWindows()
	
	#~ def setupCamara(self):
		#~ for i in xrange(self.FRAMES_CALIBRACION):
			#~ self.CAMARA.read()
			
	#~ def obtenerImagen(self):
		#~ if self.CAMARA.isOpened():
			#~ self.setupCamara()
			#~ retval, im = self.CAMARA.read()	
			#~ imtoreturn = None
			#~ if retval:
				#~ imtoreturn = base64.b64encode(cv2.imencode('.jpg',im)[1].tostring())
			#~ else:
				#~ imtoreturn = 'Error al capturar imagen'
			#~ return retval, imtoreturn
		#~ else:
			#~ return False, 'La camara no esta disponible'
import traceback
import pygame, sys
from pygame.locals import *
import pygame.camera
import base64
import datetime
import modelos
from logger import Logger
log = Logger(__name__)

class Camara(object):
	CAMARA = None
	RUTA_GUARDADO = '/home/pi/indoor-config/images/'
	
	def __init__(self):
		try:
			pygame.camera.init()
			self.CAMARA = pygame.camera.Camera("/dev/video0",(800,600))
			self.CAMARA.start()
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
	
	def __enter__(self):
		return self
		
	def __exit__(self, exc_type, exc_value, traceback_other):
		try:
			self.CAMARA.stop()
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			
	def _guardarEnDB(self, fecha):
		try:
			toadd = modelos.Foto(fecha)
			modelos.db.session.add(toadd)
			modelos.db.session.commit()
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			
	def obtenerImagen(self):
		try:
			image= self.CAMARA.get_image()
			if image is not None:
				date = datetime.datetime.now()
				full_route = self.RUTA_GUARDADO + str(date) + '.jpg'
				pygame.image.save(image, full_route)
				with open(full_route, "rb") as image_file:
					encoded_string = base64.b64encode(image_file.read())
				self._guardarEnDB(date)
				return True, encoded_string
			else:
				log.error('La camara no esta disponible')
				return False, 'La camara no esta disponible'
		except Exception, ex:
			log.exception(ex)
			print traceback.format_exc()
			return False, 'Excepcion al obtener imagen'
