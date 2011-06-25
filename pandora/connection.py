import xmlrpclib
import urllib2
import time

import crypt

class PandoraConnection(object):
	rid = ""
	lid = ""
	authInfo = {}
	authToken = ""

	PROTOCOL_VERSION = 30
	BASE_URL = "http://www.pandora.com/radio/xmlrpc/v%d?" % PROTOCOL_VERSION
	BASE_URL_RID = BASE_URL + "rid=%sP&method=%s"
	BASE_URL_LID = BASE_URL + "rid=%sP&lid=%s&method=%s"

	def __init__(self):
		self.rid = "%07i" % (time.time() % 1e7)
		
	def sync(self):
		reqUrl = self.BASE_URL_RID % (self.rid, "sync")

		req = xmlrpclib.dumps((), "misc.sync").replace("\n", "")
		enc = crypt.encryptString(req)

		u = urllib2.urlopen(reqUrl, enc)
		resp = u.read()
		u.close()

	def authListener(self, user, pwd):
		reqUrl = self.BASE_URL_RID % (self.rid, "authenticateListener")
		result = self.doRequest(reqUrl, "listener.authenticateListener", user, pwd)
		
		if not result:
			return False
		
		self.authInfo	= result
		self.authToken	= self.authInfo["authToken"]
		self.lid	= self.authInfo["listenerId"]
		return True
	
	def getStations(self):
		reqUrl = self.BASE_URL_LID % (self.rid, self.lid, "getStations")
		result = self.doRequest(reqUrl, "station.getStations", self.authToken)
		
		if not result: return None
		return result

	def getFragment(self, stationId=None, format="mp3"):
		reqUrl = self.BASE_URL_LID % (self.rid, self.lid, "getFragment")
		songlist = self.doRequest(reqUrl, "playlist.getFragment", self.authToken, stationId, "0", "", "", format, "0", "0")
		
		if not songlist: return None
		
		# last 48 chars of URL encrypted, padded w/ 8 * '\x08'
		for i in range(len(songlist)):
			url = songlist[i]["audioURL"]
			url = url[:-48] + crypt.decryptString(url[-48:])[:-8]
			songlist[i]["audioURL"] = url
		
		self.curStation = stationId
		self.curFormat = format
		
		return songlist
	
	def doRequest(self, reqUrl, method, *args):
		args = (int(time.time()), ) + args
		req = xmlrpclib.dumps(args, method).replace("\n", "")
		enc = crypt.encryptString(req)
		
		u = urllib2.urlopen(reqUrl, enc)
		resp = u.read()
		u.close()
		
		try:
			parsed = xmlrpclib.loads(resp)
		except xmlrpclib.Fault, fault:
			#print "Error:", fault.faultString
			#print "Code:", fault.faultCode
			return None
		
		return parsed[0][0]
	

if __name__ == "__main__":
	pandora = PandoraConnection()
	# pandora.sync()
	
	# read username
	print "Username: "
	username = raw_input()
	
	# read password
	print "Password: "
	password = raw_input()
	
	# authenticate
	# authenticate
	print "Authenthicated: " + str(pandora.authListener(username, password))
	
	# output stations (without QuickMix)
	print "users stations:"
	for station in pandora.getStations():
		if station['isQuickMix']: 
			quickmix = station
			continue
		print "\t" + station['stationName']
	
	# get one song from quickmix
	print "next song from quickmix:"
	next =  pandora.getFragment(quickmix)[0]['stationId']
	print next['artistSummary'] + ': ' + next['songTitle']
	print next['audioURL']
	
	# download it
	#u = urllib2.urlopen(next['audioURL'])
	#f = open('test.mp3', 'wb')
	#f.write(u.read())
	#f.close()
	#u.close()