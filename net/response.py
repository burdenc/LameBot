import re, string, socket
import util.logger_factory

logger = None

possible_responses = {
	'connect' : re.compile(r'^(?P<sender>.+) 001 .*$'), #001 connection numeric
	'ctcp' : re.compile(ur'^:(?P<sender>.+)!(?P<host>.+) (PRIVMSG|NOTICE) .+ :\u0001(?P<message>.+)\u0001$'),
	'channel_message' : re.compile(r'^:(?P<sender>.+)!(?P<host>.+) PRIVMSG (?P<channel>#.+) :(?P<message>.*)$'),
	'join' : re.compile(r'^:(?P<sender>.+)!(?P<host>.+) JOIN :?(?P<channel>#.+)$'),
	'ping' : re.compile(r'^PING (?P<sender>.+)$')
}

ctcp_commands = {
	'dcc_chat' : re.compile(r'^DCC CHAT chat (?P<dcchost>\d+) (?P<dccport>\d+)$'),
	'passive_dcc_chat' : re.compile(r'^CHAT$') #DCC Chat initiated by bot rather than user, not a part of CTCP standard
}

class Response():
	def __init__(self):
		self.logger = util.logger_factory.instance().getLogger('net.response')

	def parse(self, message):
		print message
		message = string.split(message, ' ')
		parsed = {'type':'unknown'}
		
		for response, regex in possible_responses.iteritems():
			match = regex.match(' '.join(message))
			if match:
				parsed['type'] = response
				parsed['data'] = match.groupdict()
				break
		
		if parsed['type'] == 'ctcp':
			self.logger.debug('CTCP received: %s', parsed['data']['message'])
			self._parse_ctcp(parsed)
		
		return parsed
		
	def _parse_ctcp(self, parsed):
		message = parsed['data']['message']
		for response, regex in ctcp_commands.iteritems():
			match = regex.match(message)
			if match:
				parsed['type'] = response
				parsed['data']['dcc'] = match.groupdict()
				break
		
		if parsed['type'] == 'dcc_chat':
			#Convert IPv4 integer to string
			try:
				#Convert host to hex, stripping 0x portion
				hex_host = hex(int(parsed['data']['dcchost']))[2:]
				self.logger.debug('Converting %s hex to standard IP address', hex_host)
				if hex_host[-1:] == 'L': hex_host = hex_host[:-1] #Strip trailing L
				#Convert hex to standard dot separated string
				host_str = ''
				#Group together adjacent hexadecimals into 8 byte hex
				for byte1, byte2 in zip(hex_host[0::2], hex_host[1::2]):
					host_str += str(int(byte1+byte2, 16)) #Convert 8 byte hex to decimal
					host_str += '.'
				parsed['data']['dcchost'] = host_str[:-1] #Strip trailing dot
				self.logger.debug('Integer address converted to %s', parsed['data']['dcchost'])
			except ValueError:
				self.logger.warning('Bad DCC host supplied: %s', parsed['data']['dcchost'])
				parsed['type'] = 'unknown'
				return
			
			parsed['data']['dccport'] = int(parsed['data']['dccport'])