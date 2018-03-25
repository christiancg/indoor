from distutils import util

#seteo los defaults de las variables
loggerRoute = '/tmp/indoor.log'
queueUrl = 'alfrescas.cipres.io'
queueName = 'rpc_queue'
queueUser = 'test'
queuePassword = 'ratablanca'

tiene_luz=False
tiene_bomba=False
tiene_humytemp=False
tiene_fanintra=False
tiene_fanextra=False
tiene_humtierra=False
tiene_camara=False

from os.path import expanduser
home = expanduser("~")
gpioconfig_path = home + "/indoor-config/gpio.config"
#leo la configuracion de los archivos de configuracion
try:
	with open(gpioconfig_path) as f:
		for line in f:
			if line:
				if '=' in line:
					index = line.find('=')
					if index > 0:
						parametro = line[0:index]
						valor = line[index+1:].rstrip()
						boolvalor = util.strtobool(valor)
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
