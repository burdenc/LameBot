import socket, string, time
import util.logger_factory

class Connection(object):

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.logger = util.logger_factory.instance().getLogger('net.conn.(%s:%s)' % (host, port))
	
	'''def __init__(self, socket):
		self._conn_socket = socket
		self.logger = util.logger_factory.instance().getLogger('net.conn.(%s:%s)' % socket.getpeername())'''
	
	def connect(self, host = None, port = None, no_buffer = True):
		if host == None or port == None:
			host = self.host
			port = self.port
		
		self.logger.debug('Connecting to %s on port %s', host, port)
		
		self._conn_socket = socket.socket()
		
		if no_buffer:
			self._conn_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			
		self._conn_socket.connect((host, port))
		
		self.logger.info('Established socket connection with %s on port %s', host, port)
		
	def disconnect(self, how = socket.SHUT_RDWR):
		self._conn_socket.shutdown(how)
		self._conn_socket.close()
		
	def poll(self):
		buffer = self._conn_socket.recv(1024)
		if buffer == '':
			self.logger.info('Connection closed by peer')
			self.disconnect()
			raise ConnectionClosedError()
		buffer = string.rstrip(buffer)
		buffer = string.split(buffer, '\r\n')
		return buffer
	
	#Used to comply with select.select()
	def fileno(self):
		return self._conn_socket.fileno()
		
	def get_ext_address(self):
		return self._conn_socket.getsockname()
		
	def _send_raw(self, message):
		if message[-2:] != '\r\n':
			message += '\r\n'
		self.logger.debug('SENDING: %s', message[:-2])
		sent = self._conn_socket.sendall(message)
		
class ConnectionClosedError(Exception):
	pass