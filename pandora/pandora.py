import urllib2

from connection import PandoraConnection

class Pandora(object):
	stationId = None
	authenticated = False
	backlog = []
	
	def __init__(self):
		self.connection = PandoraConnection()
	
	def authenticate(self, username, password):
		self.authenticated = self.connection.authListener(username, password)
		return self.authenticated
		
	def getStationList(self):
		return self.connection.getStations()
	
	def switchStation(self, stationId):
		if type(stationId) is dict:
			stationId = stationId['stationId']
		
		if not self.authenticated: raise ValueError("User not yet authenticated")
		
		self.backlog = []
		self.stationId = stationId
		self.backlog = self.connection.getFragment(stationId) + self.backlog
	
	def getNextSong(self):
		if not self.authenticated: raise ValueError("User not yet authenticated")
		if not self.stationId: raise ValueError("No station selected")
		
		# get more songs
		if len(self.backlog) < 2:
			self.backlog = self.connection.getFragment(self.stationId) + self.backlog
		
		# get next song
		return self.backlog.pop()
		
		
if __name__ == "__main__":
	pandora = Pandora()
	
	# read username
	print "Username: "
	username = raw_input()
	
	# read password
	print "Password: "
	password = raw_input()
	
	# authenticate
	print "Authenthicated: " + str(pandora.authenticate(username, password))
	
	# output stations (without QuickMix)
	print "users stations:"
	for station in pandora.getStationList():
		if station['isQuickMix']: 
			quickmix = station
			continue
		print "\t" + station['stationName']
	
	# switch to quickmix station
	pandora.switchStation(quickmix)
	
	# get one song from quickmix
	print "next song from quickmix:"
	next =  pandora.getNextSong()
	print next['artistSummary'] + ': ' + next['songTitle']
	print next['audioURL']
	
	# download it
	#u = urllib2.urlopen(next['audioURL'])
	#f = open('test.mp3', 'wb')
	#f.write(u.read())
	#f.close()
	#u.close()