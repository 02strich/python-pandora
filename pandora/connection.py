import json
import urllib
import urllib2
import sys
import time

from .crypt import pandora_decrypt, pandora_encrypt


class AuthenticationError(Exception):
    """Raised when an operation encountered authentication issues."""
    pass


class PandoraConnection(object):
    """Connection to the Pandora API without a specific user context"""

    partner_id = None
    partner_auth_token = None

    time_offset = None

    PROTOCOL_VERSION = '5'
    RPC_URL = "://internal-tuner.pandora.com/services/json/?"
    DEVICE_MODEL = 'D01'
    PARTNER_USERNAME = 'pandora one'
    PARTNER_PASSWORD = 'TVCKIBGS9AO9TSYLNNFUML0743LH82D'

    def __init__(self):
        self.rid = "%07i" % (time.time() % 1e7)
        self.timedelta = 0

        try:
            # partner login
            partner = self.do_request('auth.partnerLogin', True, False, {},
                                      deviceModel=self.DEVICE_MODEL,
                                      username=self.PARTNER_USERNAME,
                                      password=self.PARTNER_PASSWORD,
                                      version=self.PROTOCOL_VERSION)
            self.partner_id = partner['partnerId']
            self.partner_auth_token = partner['partnerAuthToken']

            # sync
            pandora_time = int(pandora_decrypt(partner['syncTime'])[4:14])
            self.time_offset = pandora_time - time.time()
        except Exception as e:
            self.partner_id = None
            self.partner_auth_token = None
            self.time_offset = None

            raise Exception("Establishing connection to Pandora failed: %s" % str(e)), None, sys.exc_info()[2]

    def authenticate_user(self, user, pwd):
        try:
            return self.do_request('auth.userLogin', True, True, {}, username=user, password=pwd, loginType="user", returnStationList=True)
        except:
            return None

    def search(self, user, text):
        return self.do_request("music.search", False, True, user, searchText=text)

    def get_stations(self, user):
        return self.do_request('user.getStationList', False, True, user)['stations']

    def get_genre_stations(self, user):
        return self.do_request("station.getGenreStations", False, True, user)

    def get_fragment(self, user, station):
        return self.do_request('station.getPlaylist', True, True, user, stationToken=station['stationToken'])['items']

    def get_station(self, user, station):
        return self.do_request('station.getStation', False, True, user, stationToken=station['stationToken'], includeExtendedAttributes=True)

    def delete_station(self, user, station):
        self.do_request('station.deleteStation', False, True, user, stationToken=station['stationToken'])

    def add_seed(self, user, station, song_or_artist):
        return self.do_request('station.addMusic', False, True, user, stationToken=station['stationToken'], musicToken=song_or_artist['musicToken'])

    def delete_seed(self, user, station, song_or_artist):
        self.do_request("station.deleteMusic", False, True, user, seedId=song_or_artist['seedId'])

    def add_feedback(self, user, station, track, is_positive_feedback=True):
        return self.do_request("station.addFeedback", False, True, user,
                               stationToken=station['stationToken'],
                               trackToken=track['trackToken'],
                               isPositive=is_positive_feedback)

    def delete_feedback(self, user, station, feedback):
        self.do_request("station.deleteFeedback", False, True, user, feedbackId=feedback['feedbackId'])

    def do_request(self, method, secure, crypted, user, **kwargs):
        url_arg_strings = []
        if self.partner_id:
            url_arg_strings.append('partner_id=%s' % self.partner_id)
        if 'userId' in user:
            url_arg_strings.append('user_id=%s' % user['userId'])
        if 'userAuthToken' in user:
            url_arg_strings.append('auth_token=%s' % urllib.quote_plus(user['userAuthToken']))
        elif self.partner_auth_token:
            url_arg_strings.append('auth_token=%s' % urllib.quote_plus(self.partner_auth_token))

        url_arg_strings.append('method=%s' % method)
        url = ('https' if secure else 'http') + self.RPC_URL + '&'.join(url_arg_strings)

        if self.time_offset:
            kwargs['syncTime'] = int(time.time() + self.time_offset)
        if 'userAuthToken' in user:
            kwargs['userAuthToken'] = user['userAuthToken']
        elif self.partner_auth_token:
            kwargs['partnerAuthToken'] = self.partner_auth_token
        data = json.dumps(kwargs)

        if crypted:
            data = pandora_encrypt(data)

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
