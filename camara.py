import cv2
import base64

class Camara(object):
	FRAMES_CALIBRACION = 0
	CAMARA = None
	
	def __init__(self, framescalibracion):
		self.FRAMES_CALIBRACION = framescalibracion
		self.CAMARA = cv2.VideoCapture(0)
		if not self.CAMARA.isOpened():
			self.CAMARA.release()
			self.CAMARA = cv2.VideoCapture(-1)
	
	def __enter__(self):
		return self
		
	def __exit__(self, exc_type, exc_value, traceback):
		self.CAMARA.release()
		cv2.destroyAllWindows()
	
	def setupCamara(self):
		for i in xrange(self.FRAMES_CALIBRACION):
			self.CAMARA.read()
			
	def obtenerImagen(self):
		if self.CAMARA.isOpened():
			self.setupCamara()
			retval, im = self.CAMARA.read()	
			imtoreturn = None
			if retval:
				imtoreturn = base64.b64encode(cv2.imencode('.jpg',im)[1].tostring())
			else:
				imtoreturn = 'Error al capturar imagen'
			return retval, imtoreturn
		else:
			return False, 'La camara no esta disponible'
