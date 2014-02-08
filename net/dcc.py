import socket
import util.logger_factory
from net.connection import Connection

class DCC(Connection):
	def __init__(self, host, port, passive):
		self.host = host
		self.port = port
		self.logger = util.logger_factory.instance().getLogger('net.DCC.(%s:%s)' % (host, port))
		
	def __init__(self, socket):
		self._conn_socket = socket
		self.logger = util.logger_factory.instance().getLogger('net.DCC.(%s:%s)' % socket.getpeername())