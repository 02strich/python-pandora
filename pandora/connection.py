import json
import urllib
import urllib2
import time

import crypt

class AuthenticationError(Exception):
	"""Raised when an operation encountered authentication issues."""
	pass

class PandoraConnection(object):
	partner_id = None
	partner_auth_token = None
	
	user_id = None
	user_auth_token = None
	
	time_offset = None
	
	PROTOCOL_VERSION = '5'
	RPC_URL = "://tuner.pandora.com/services/json/?"
	DEVICE_MODEL = 'android-generic'
	PARTNER_USERNAME = 'android'
	PARTNER_PASSWORD = 'AC7IBG09A3DTSYM4R41UJWL07VLN8JI7'
	
	def __init__(self):
		self.rid = "%07i" % (time.time() % 1e7)
		self.timedelta = 0
		
	def authenticate(self, user, pwd):
		try:
			# partner login
			partner = self.do_request('auth.partnerLogin', True, False, deviceModel=self.DEVICE_MODEL, username=self.PARTNER_USERNAME, password=self.PARTNER_PASSWORD, version=self.PROTOCOL_VERSION)
			self.partner_id = partner['partnerId']
			self.partner_auth_token = partner['partnerAuthToken']
			
			# sync
			pandora_time = int(crypt.pandora_decrypt(partner['syncTime'])[4:14])
			self.time_offset = pandora_time - time.time()
			
			# user login
			user = self.do_request('auth.userLogin', True, True, username=user, password=pwd, loginType="user")
			self.user_id = user['userId']
			self.user_auth_token = user['userAuthToken']
			
			return True
		except:
			self.partner_id = None
			self.partner_auth_token = None
			self.user_id = None
			self.user_auth_token = None
			self.time_offset = None
			
			return False
	
	def get_stations(self):
		return self.do_request('user.getStationList', False, True)['stations']
	
	def get_fragment(self, stationId=None, format="mp3"):
		songlist = self.do_request('station.getPlaylist', True, True, stationToken=stationId, additionalAudioUrl='HTTP_64_AACPLUS_ADTS,HTTP_128_MP3,HTTP_192_MP3')['items']
				
		self.curStation = stationId
		self.curFormat = format
		
		return songlist
	
	def do_request(self, method, secure, crypted, **kwargs):
		url_arg_strings = []
		if self.partner_id:
			url_arg_strings.append('partner_id=%s' % self.partner_id)
		if self.user_id:
			url_arg_strings.append('user_id=%s' % self.user_id)
		if self.user_auth_token:
			url_arg_strings.append('auth_token=%s'%urllib.quote_plus(self.user_auth_token))
		elif self.partner_auth_token:
			url_arg_strings.append('auth_token=%s' % urllib.quote_plus(self.partner_auth_token))
		
		url_arg_strings.append('method=%s'%method)
		url = ('https' if secure else 'http') + self.RPC_URL + '&'.join(url_arg_strings)
		
		if self.time_offset:
			kwargs['syncTime'] = int(time.time()+self.time_offset)
		if self.user_auth_token:
			kwargs['userAuthToken'] = self.user_auth_token
		elif self.partner_auth_token:
			kwargs['partnerAuthToken'] = self.partner_auth_token
		data = json.dumps(kwargs)
		
		if crypted:
			data = crypt.pandora_encrypt(data)

		# execute request
		req = urllib2.Request(url, data, {'User-agent': "02strich", 'Content-type': 'text/plain'})
		response = urllib2.urlopen(req)
		text = response.read()

		# parse result
		tree = json.loads(text)
		if tree['stat'] == 'fail':
			code = tree['code']
			msg = tree['message']
			if code == 1002:
				raise AuthenticationError()
			else:
				raise ValueError("%d: %s" % (code, msg))
		elif 'result' in tree:
			return tree['result']
			

if __name__ == "__main__":
	pandora = PandoraConnection()
	
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
	for station in pandora.getStations():
		if station['isQuickMix']: 
			quickmix = station
			print "\t" + station['stationName'] + "*"
		else:
			print "\t" + station['stationName']
	
	# get one song from quickmix
	print "next song from quickmix:"
	next =  pandora.getFragment(quickmix)[0]
	print next['artistName'] + ': ' + next['songName']
	print next['audioUrlMap']['highQuality']['audioUrl']
	
	# download it
	#u = urllib2.urlopen(next['audioUrlMap']['highQuality']['audioUrl'])
	#f = open('test.mp3', 'wb')
	#f.write(u.read())
	#f.close()
	#u.close()