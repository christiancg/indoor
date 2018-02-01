from functools import wraps
from flask import request, Response
from modelos import Usuario

from logger import Logger
log = Logger(__name__)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    try:
		usr = Usuario.query.filter(Usuario.nombre == username).first()
		if usr is None:
			return False
		elif usr.password != password:
			return False
		else:
			return True
    except Exception, ex:
		log.exception(ex)
		return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
