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
	
	def call_event(self, event_name, data, network):
		#try:
		if event_name not in self._registered:
			return
		
		for priority, obj, func in sorted(self._registered[event_name], reverse=True):
			#Test to see if extension enabled in channel
			ext_name = obj.__class__.__name__
			if ext_name not in network['global_extensions']:
				try:
					if data['channel'] not in network['ext'][ext_name]['channels']:
						continue
				except KeyError, TypeError:
					pass
			
			print 'CALLING %s for %s' % (func, event_name)
			result = func(obj, data, network)
			if result is Result.PREVENT_ALL:
				return
		#except:
			#pass
