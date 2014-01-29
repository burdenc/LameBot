import re, string, socket
import util.logger_factory

logger = None

possible_responses = {
	'connect' : re.compile(r'^(?P<sender>.+) 001 .*$'), #001 connection numeric
	'channel_message' : re.compile(r'^:(?P<sender>.+)!(?P<host>.+) PRIVMSG (?P<channel>#.+) :(?P<message>.*)$'),
	'join' : re.compile(r'^:(?P<sender>.+)!(?P<host>.+) JOIN :?(?P<channel>#.+)$'),
	'ping' : re.compile(r'^PING (?P<sender>.+)$')
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
		
		return parsed