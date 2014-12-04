import getpass

from .pandora import Pandora
from .connection import PandoraConnection


def pandora_main():
    # read username
    username = raw_input("Username: ")

    # read password
    password = getpass.getpass()

    # read proxy config
    proxy = raw_input("Proxy: ")
    if proxy:
        proxy_support = urllib2.ProxyHandler({"http": proxy, "https": proxy})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

    pandora = Pandora()

    # authenticate
    print "Authenthicated: " + str(pandora.authenticate(username, password))

    # output stations (without QuickMix)
    print "users stations:"
    for station in pandora.stations:
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
    if False:
        u = urllib2.urlopen(next['audioUrlMap']['highQuality']['audioUrl'])
        f = open('test.mp3', 'wb')
        f.write(u.read())
        f.close()
        u.close()


def connection_main():
    conn = PandoraConnection()

    # read username
    username = raw_input("Username: ")

    # read password
    password = getpass.getpass("Password: ")

    # authenticate
    user = conn.authenticate_user(username, password)
    print "Authenticated: " + str(user)

    if user is not None:
        # output stations (without QuickMix)
        print "users stations:"
        for station in conn.get_stations(user):
            if station['isQuickMix']:
                quickmix = station
                print "\t" + station['stationName'] + "*"
            else:
                print "\t" + station['stationName']

        # get one song from quickmix
        print "next song from quickmix:"
        next = conn.get_fragment(user, quickmix)[0]
        print next['artistName'] + ': ' + next['songName']
        print next['audioUrlMap']['highQuality']['audioUrl']

        # download it
        if False:
            u = urllib2.urlopen(next['audioUrlMap']['highQuality']['audioUrl'])
            f = open('test.mp3', 'wb')
            f.write(u.read())
            f.close()
            u.close()


if __name__ == "__main__":
    #pandora_main()
    connection_main()
