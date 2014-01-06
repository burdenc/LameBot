#TODO: change api to allow multiple server connections
#TODO: use pyconf to load in servers to connect to, nick info, etc.
#TODO: flesh out irc.py api

import net.irc, api.scheduler, api.loader
import sys, string, time, sqlite3, ConfigParser, collections

class Bot():
	def __init__(self, conf_file):
		self._parse_config(conf_file)

		conn = sqlite3.connect('bot.db')

		for network in self.network_list.itervalues():
			connection = net.irc.IRC()
			connection.connect(
				network['address'],
				network['port'],
				network['nick'],
				network['real_name'],
				network['channels']
			)
			network['connection'] = connection

		scheduler = api.scheduler.Scheduler()
		loader = api.loader.Loader(scheduler, freenode, conn)
		loader.load_all()


	def run(self):
		while True:
			for line in freenode.poll():
				line = string.rstrip(line)
				#not whitespace
				if line:
					response = net.irc.Response.parse(line)
					if response['type'] != 'unknown':
						if response['data']: data = response['data']
						else: data = None
						scheduler.call_event(response['type'], data)
						conn.commit()
					#print response
					if response['type'] == 'connect':
						freenode.join()
					if response['type'] == 'ping':
						freenode._send_raw(net.irc.Commands.PONG(response['data']['sender']))
					
	def _parse_config(self, conf_file):
		config = ConfigParser.ConfigParser()
		config.read([conf_file])
		defaults = config.items('Global')
		config._defaults = collections.OrderedDict(defaults)
		
		self.network_list = {}
		for section in config.sections():
			if section == 'Global': continue
			items = config.items(section)
			self.network_list[section] = dict(items)
	
if __name__ == '__main__':
	try:
		conf_file = sys.argv[1]
	except IndexError:
		conf_file = 'bot.conf'
	
	bot = Bot(conf_file)
	bot.run()