import xmlrpclib
import urllib2
import time

import crypt

PROTOCOL_VERSION = 30
BASE_URL = "http://www.pandora.com/radio/xmlrpc/v%d?" % PROTOCOL_VERSION
BASE_URL_RID = BASE_URL + "rid=%sP&method=%s"
BASE_URL_LID = BASE_URL + "rid=%sP&lid=%s&method=%s"

def _inttime():
	return int(time.time())

class Pandora(object):
	rid = ""
	lid = ""
	authInfo = {}
	authToken = ""
	curStation = ""
	curFormat = "mp3" # Default to mp3 if not specified

	def __init__(self, format="mp3"):
		self.rid = "%07i" % (time.time() % 1e7)
		self.curFormat = format
		
		# configure urllib2
		proxy_support = urllib2.ProxyHandler({"http" : "http://us-vpn.02strich.de:8888"})
		
		opener = urllib2.build_opener(proxy_support)
		urllib2.install_opener(opener)

	def sync(self):
		reqUrl = BASE_URL_RID % (self.rid, "sync")

		req = xmlrpclib.dumps((), "misc.sync").replace("\n", "")
		enc = crypt.encryptString(req)

		u = urllib2.urlopen(reqUrl, enc)
		resp = u.read()
		u.close()

	def authListener(self, user, pwd):
		reqUrl = BASE_URL_RID % (self.rid, "authenticateListener")

		req = xmlrpclib.dumps(( _inttime(), user, pwd ), "listener.authenticateListener").replace("\n", "")
		enc = crypt.encryptString(req)

		u = urllib2.urlopen(reqUrl, enc)
		resp = u.read()
		u.close()

		try:
			self.authInfo = xmlrpclib.loads(resp)[0][0]
		except xmlrpclib.Fault, fault:
			#print "Error:", fault.faultString
			#print "Code:", fault.faultCode
			return False

		self.authToken	= self.authInfo["authToken"]
		self.lid		= self.authInfo["listenerId"]
		
		return True
	
	def getStations(self):
		reqUrl = BASE_URL_LID % (self.rid, self.lid, "getStations")

		req = xmlrpclib.dumps(( _inttime(), self.authToken ), "station.getStations").replace( "\n", "" )
		enc = crypt.encryptString(req)

		u = urllib2.urlopen(reqUrl, enc)
		resp = u.read()
		u.close()

		parsed = xmlrpclib.loads(resp)[0][0]

		return parsed

	def getFragment(self, stationId=None, format=None):
		if stationId == None:
			stationId = self.curStation
		elif type(stationId) is dict:
			stationId = stationId['stationId']
		if format == None:
			format = self.curFormat
		reqUrl = BASE_URL_LID % (self.rid, self.lid, "getFragment")

		args = (_inttime(), self.authToken, stationId, "0", "", "", format, "0", "0")
		req = xmlrpclib.dumps(args, "playlist.getFragment").replace("\n", "")
		enc = crypt.encryptString(req)

		u = urllib2.urlopen(reqUrl, enc)
		resp = u.read()
		u.close()

		parsed = xmlrpclib.loads(resp)[0][0]

		#last 48 chars of URL encrypted, padded w/ 8 * '\x08'
		for i in range(len(parsed)):
			url = parsed[i]["audioURL"]
			url = url[:-48] + crypt.decryptString(url[-48:])[:-8]
			parsed[i]["audioURL"] = url

		self.curStation = stationId
		self.curFormat = format

		return parsed

if __name__ == "__main__":
	pandora = Pandora()
	# pandora.sync()
	
	# read username
	print "Username: "
	username = raw_input()
	
	# read password
	print "Password: "
	password = raw_input()
	
	# authenticate
	pandora.authListener(username, password)
	
	# output stations (without QuickMix)
	print "users stations:"
	for station in pandora.getStations():
		if station['isQuickMix']: 
			quickmix = station
			continue
		print "\t" + station['stationName']
	
	# get one song from quickmix
	print "next song from quickmix:"
	next =  pandora.getFragment(quickmix)[0]
	print next['artistSummary'] + ': ' + next['songTitle']
	print next['audioURL']
	
	# download it
	#u = urllib2.urlopen(next['audioURL'])
	#f = open('test.mp3', 'wb')
	#f.write(u.read())
	#f.close()
	#u.close()