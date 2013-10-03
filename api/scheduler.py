from api.plugin import Result, Priority

class Scheduler():
	
	def __init__(self):
		self._registered = {}
	
	def register_event(self, event_name, obj, func, priority = Priority.NORMAL):
		print 'REGISTERING %s for %s' % (event_name, func)
		try:
			self._registered[event_name] += [(priority, obj, func)]
		except KeyError:
			self._registered[event_name] = [(priority, obj, func)]
	
	def call_event(self, event_name, data):
		try:
			for priority, obj, func in sorted(self._registered[event_name], reverse=True):
				print 'CALLING %s for %s' % (func, event_name)
				result = func(obj, data)
				if result is Result.PREVENT_ALL:
					return
		except:
			pass
