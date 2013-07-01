import urllib2

from connection import PandoraConnection


def authenticated(f):
    def check_authentication(self, *args):
        if not self.is_authenticated:
            raise ValueError("User not yet authenticated")
        return f(self, *args)
    return check_authentication


class Pandora(object):
    station_id = None
    is_authenticated = False
    backlog = []

    def __init__(self):
        self.connection = PandoraConnection()

    def authenticate(self, username, password):
        self.is_authenticated = self.connection.authenticate(username, password)
        return self.is_authenticated

    @authenticated
    def search(self, text):
        return self.connection.search(text)

    @authenticated
    def get_station_list(self):
        return self.connection.get_stations()

    @authenticated
    def get_genre_stations(self):
        return self.connection.get_genre_stations()

    @authenticated
    def get_station(self, station_token):
        return self.connection.get_station(station_token)

    @authenticated
    def delete_station(self, station_token):
        self.connection.delete_station(station_token)

    @authenticated
    def add_seed(self, station_token, music_token):
        return self.connection.add_seed(station_token, music_token)

    @authenticated
    def delete_seed(self, station_token, seed_token):
        self.connection.delete_seed(station_token, seed_token)

    @authenticated
    def add_feedback(self, station_token, track_token, is_positive_feedback=True):
        return self.connection.add_feedback(station_token, track_token, is_positive_feedback)

    @authenticated
    def delete_feedback(self, station_token, feedback_token):
        self.connection.delete_feedback(station_token, feedback_token)

    @authenticated
    def switch_station(self, station_id):
        if type(station_id) is dict:
            station_id = station_id['stationId']

        self.backlog = []
        self.station_id = station_id
        self.backlog = self.connection.get_fragment(station_id) + self.backlog

    @authenticated
    def get_next_song(self):
        if not self.station_id:
            raise ValueError("No station selected")

        # get more songs
        if len(self.backlog) < 2:
            self.backlog = self.connection.get_fragment(self.station_id) + self.backlog

        # get next song
        return self.backlog.pop()


if __name__ == "__main__":
    import getpass
    pandora = Pandora()

    # read username
    username = raw_input("Username: ")

    # read password
    password = getpass.getpass()

    # read proxy config
    proxy = raw_input("Proxy: ")
    if proxy:
        proxy_support = urllib2.ProxyHandler({"http": proxy})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

    # authenticate
    print "Authenthicated: " + str(pandora.authenticate(username, password))

    # output stations (without QuickMix)
    print "users stations:"
    for station in pandora.get_station_list():
        if station['isQuickMix']:
            quickmix = station
            print "\t" + station['stationName'] + "*"
        else:
            print "\t" + station['stationName']

    # switch to quickmix station
    pandora.switch_station(quickmix)

    # get one song from quickmix
    print "next song from quickmix:"
    next = pandora.get_next_song()
    print next['artistName'] + ': ' + next['songName']
    print next['audioUrlMap']['highQuality']['audioUrl']

    # download it
    #u = urllib2.urlopen(next['audioUrlMap']['highQuality']['audioUrl'])
    #f = open('test.mp3', 'wb')
    #f.write(u.read())
    #f.close()
    #u.close()
