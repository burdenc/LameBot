from api.plugin import Result, Priority
from util import logger_factory

class Scheduler():
	
	def __init__(self):
		self._registered = {}
		self.logger = logger_factory.instance().getLogger('api.scheduler')
	
	def register_event(self, event_name, obj, func, priority = Priority.NORMAL):
		self.logger.debug('Registering %s for %s', func, event_name)
		try:
			self._registered[event_name] += [(priority, obj, func)]
		except KeyError:
			self._registered[event_name] = [(priority, obj, func)]
	
	def call_event(self, event_name, data, network):
		self.logger.debug('Calling event %s for network %s with data %s', event_name, network.name, data)
	
		#try:
		if event_name not in self._registered:
			return
		
		for priority, obj, func in sorted(self._registered[event_name], reverse=True):
			#Test to see if extension enabled in channel
			ext_name = obj.__class__.__name__
			if ext_name not in network.extensions:
				try:
					if data['channel'] not in network.allowed_channels[ext_name]:
						continue
				except KeyError, TypeError:
					pass
			
			print 'CALLING %s for %s' % (func, event_name)
			result = func(obj, data, network)
			if result is Result.PREVENT_ALL:
				return
		#except:
			#pass
