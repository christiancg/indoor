from distutils import util
import uuid

#seteo los defaults de las variables
loggerRoute = '/tmp/indoor.log'
queueUrl = 'shop.cipres.io'
queueName = str(uuid.uuid4())
queueUser = 'birritas'
queuePassword = 'fresquitas'

tiene_luz=False
tiene_bomba=False
tiene_humytemp=False
tiene_fanintra=False
tiene_fanextra=False
tiene_humtierra=False
tiene_camara=False

users = []

from os.path import expanduser
home = expanduser("~")
gpioconfig_path = home + "/indoor-config/gpio.config"
serverconfig_path = home + "/indoor-config/server.config"
usersconfig_path = home + "/indoor-config/users.config"

def leerConfigGpio():
	global tiene_luz
	global tiene_bomba
	global tiene_humytemp
	global tiene_fanintra
	global tiene_fanextra
	global tiene_humtierra
	global tiene_camara
	try:
		with open(gpioconfig_path) as f:
			for line in f:
				if line:
					if '=' in line:
						index = line.find('=')
						if index > 0:
							parametro = line[0:index]
							valor = line[index+1:].rstrip()
							try:
								boolvalor = util.strtobool(valor)
							except:
								print 'Error al leer el valor del parametro: ' + parametro + '. Los valores validos son true o false -> recibido: ' + valor
								boolvalor = False
							print parametro + ' ' + valor
							if parametro == 'luz':
								tiene_luz=boolvalor
							elif parametro == 'bomba':
								tiene_bomba=boolvalor
							elif parametro == 'humytemp':
								tiene_humytemp=boolvalor
							elif parametro == 'fanintra':
								tiene_fanintra=boolvalor
							elif parametro == 'fanextra':
								tiene_fanextra=boolvalor
							elif parametro == 'humtierra':
								tiene_humtierra=boolvalor
							elif parametro == 'camara':
								tiene_camara=boolvalor
	except Exception, ex:
		import traceback
		print traceback.format_exc()
		
def leerConfigServer():
	global queueUrl
	global queueName
	global queueUser
	global queuePassword
	try:
		with open(serverconfig_path) as f:
			for line in f:
				if line:
					if '=' in line:
						index = line.find('=')
						if index > 0:
							parametro = line[0:index]
							valor = line[index+1:].rstrip()
							print parametro + ' ' + valor
							if parametro == 'queueUrl':
								queueUrl=valor
							elif parametro == 'queueName':
								if not valor=='random':
									queueName=valor
							elif parametro == 'queueUser':
								queueUser=valor
							elif parametro == 'queuePassword':
								queuePassword=valor
	except Exception, ex:
		import traceback
		print traceback.format_exc()
		
def leerUsers():
	global users
	try:
		with open(usersconfig_path) as f:
			for line in f:
				if line:
					if '=' in line:
						index = line.find('=')
						if index > 0:
							user = line[0:index]
							password = line[index+1:].rstrip()
							print user + ' ' + password
							users.append((user,password))
	except Exception, ex:
		import traceback
		print traceback.format_exc()
		
#leo la configuracion gpio del archivo de configuracion
leerConfigGpio()
#leo la configuracion de server del archivo de configuracion
leerConfigServer()
#leo los usuarios del archivo de configuracion
leerUsers()
