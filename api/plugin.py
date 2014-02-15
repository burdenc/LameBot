from abc import ABCMeta, abstractmethod

class Priority():
	MAX = 5
	HIGH = 4
	NORMAL = 3
	LOW = 2
	LOG = 1
	
class Result():
	PREVENT_ALL = 3
	PREVENT_DEFAULT = 2
	PREVENT_PLUGINS = 1
	SUCCESS = None

#Abstract class, do not instantiate
class Plugin():
	__metaclass__ = ABCMeta

	def __init__(self, scheduler, network_list, sql, logger):
		self.api = network_list
		self.sql = sql
		self._scheduler = scheduler
		self.logger = logger
		
	def register_event(self, event_name, func, priority = Priority.NORMAL):
		self._scheduler.register_event(event_name, self, func, priority)
	
	@abstractmethod
	def _install_(self):
		pass
		
	@abstractmethod
	def _start_(self):
		pass
	
	@abstractmethod
	def _uninstall_(self):
		pass