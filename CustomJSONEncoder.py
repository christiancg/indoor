from sqlalchemy.ext.declarative import DeclarativeMeta
import json
import traceback
from datetime import datetime,time

class CustomJSONEncoder(json.JSONEncoder):
	def default(self,obj):
		try:
			if hasattr(obj, '__iter__'):
				for x in obj:
					return self.xitem(x)
			else:
				return self.xitem(obj)
		except Exception,ex:
			print traceback.format_exc()
			return ex

	def xitem(self,obj):
			if isinstance(obj.__class__, DeclarativeMeta):
				data={}
				fields = dir(obj)
				for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
					value = obj.__getattribute__(field)
					data[field] = value
					try:
						json.dumps(value)
						data[field] = value
					except TypeError:
						if isinstance(value,datetime):
							data[field] = value.isoformat()
						elif isinstance(value,time):
							data[field] = value.strftime('%H:%M:%S')
						elif isinstance(value.__class__, DeclarativeMeta):
							data[field] = self.default(value)
						else: data[field] = None
				return data
			return json.JSONEncoder.default(self,obj)
