#import run
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
#from sqlalchemy.ext.declarative import DeclarativeMeta

#from CustomJSONEncoder import CustomJSONEncoder

#db = SQLAlchemy(run.app)
db = SQLAlchemy()


#class Serializer(object):
#	def serialize(self):
#		cust = CustomJSONEncoder(self)
#		return cust.default(self)
		#return {c: (serialize(c) if isinstance(c.__class__, DeclarativeMeta) else  getattr(self,c)) for c in inspect(self).attrs.keys()}
		#return {c: getattr(self,c) for c in inspect(self).attrs.keys()}
#	@staticmethod
#	def serialize_list(l):
#		return [m.serialize() for m in l]

class Evento(db.Model):
	__tablename__ = 'eventos'
	id = db.Column(db.Integer, primary_key=True)
	fechayhora = db.Column(db.DateTime)
	desc = db.Column(db.String(100))
	configgpio_id = db.Column(db.Integer, db.ForeignKey('configsgpio.id'))
	configgpio = db.relationship('ConfigGpio')
	
	def __init__(self,fechayhora,desc,configgpio):
		self.fechayhora = fechayhora
		self.desc = desc
		self.configgpio = configgpio
	def __repr__(self):
		return '<Evento %r>' % self.id
			
class ConfigGpio(db.Model):
	__tablename__ = 'configsgpio'
	id = db.Column(db.Integer, primary_key=True)
	desc = db.Column(db.String(15))
	estado = db.Column(db.Boolean)
	def __init__(self,id,desc):
		self.id = id
		self.desc = desc
		self.estado = False
	def __repr__(self):
		return '<ConfigGpio %r>' % self.id	
		
class Programacion(db.Model):
	__tablename__ = 'programaciones'
	id = db.Column(db.Integer, primary_key=True)
	desc = db.Column(db.String(100))
	configgpio_id = db.Column(db.Integer, db.ForeignKey('configsgpio.id'))
	configgpio = db.relationship('ConfigGpio')
	prender = db.Column(db.Boolean)
	horario1 = db.Column(db.Time)
	duracion = db.Column(db.Integer)
	habilitado = db.Column(db.Boolean)
	def __init__(self,desc,configgpio,prender,horario1,duracion=None):
		self.desc = desc
		self.configgpio = configgpio
		self.prender = prender
		self.horario1 = horario1
		if duracion is not None:
			self.duracion = duracion
		self.habilitado = True
	def __repr__(self):
		return '<Programacion %r>' % self.id
		
class Usuario(db.Model):
	__tablename__ = 'usuarios'
	nombre = db.Column(db.String(50), primary_key=True)
	password = db.Column(db.String(100))
	def __init__(self,nombre,password):
		self.nombre = nombre
		self.password = password
	def __repr__(self):
		return '<Usuario %r>' % self.nombre
		
class Foto(db.Model):
	__tablename__ = 'fotos'
	fecha = db.Column(db.DateTime, primary_key=True)
	def __init__(self,fecha):
		self.fecha = fecha
	def __repr__(self):
		return '<Foto %r>' % self.fecha
		

