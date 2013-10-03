#TODO: change api to allow multiple server connections
#TODO: use pyconf to load in servers to connect to, nick info, etc.
#TODO: flesh out irc.py api

import net.irc, api.scheduler, api.loader
import string, time, sqlite3

conn = sqlite3.connect('bot.db')

freenode = net.irc.IRC()
freenode.connect('irc.quakenet.org', 6667, 'DeltaburntBot', 'My bot', ['#deltaburnt'])

scheduler = api.scheduler.Scheduler()
loader = api.loader.Loader(scheduler, freenode, conn)
loader.load_all()


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