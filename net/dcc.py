import socket
import util.logger_factory

class DCC():
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.logger = util.logger_factory.instance().getLogger('DCC.%s:%s' % (host, port))
	
	def connect(self):
		self._conn_socket = socket.socket()
		self.logger.debug('Connecting to remote host')
		self._conn_socket.connect((self.host, self.port))
	
	def poll(self):
		buffer = self._conn_socket.recv(1024)
		buffer = string.rstrip(buffer)
		buffer = string.split(buffer, '\r\n')
		return buffer
	
	#Used to comply with select.select()
	def fileno(self):
		return self._conn_socket.fileno()
		
	def _send_raw(self, message):
		if message[1] != '\x01':
			message = '\x01'+message
		if message[-1] != '\x01':
			message = message+'\x01'
		if message[-2:] != '\r\n':
			message += '\r\n'
		self.logger.debug('SENDING: %s', message[1:-3])
		sent = self._conn_socket.sendall(message)	