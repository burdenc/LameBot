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
		
#Used to create DCC object once incoming socket connection is accepted
class DCCPassive(Connection):
	def __init__(self, host = '', port = 0):
		self.host = host
		self.port = port
		
	def bind(self):
		self._conn_socket = socket.socket()
		self._conn_socket.bind((self.host, self.port)) #Bind to any available IP and port
		self.host, self.port = self.get_ext_address()
		self.logger = util.logger_factory.instance().getLogger('net.DCCPassive.(%s:%s)' % (self.host, self.port))
		
		self._conn_socket.listen(1) #Listen for connections, only one connection per DCC socket
		self.logger.info('Listening for socket Connection')
	
	def accept(self):
		client_socket, address = self._conn_socket.accept()
		self.logger.info('Accepting connection from %s:%s' % address)
		return client_socket
	
def ip_to_int(ip_addr):
	bytes = socket.inet_aton(ip_addr)
	bytes = bytes.encode('hex_codec') #Convert from literal byte (ex '\x01') to ascii hex ('01')
	return int(bytes, 16) #Convert hex bytes to int