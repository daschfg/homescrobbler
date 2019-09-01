#!/usr/bin/python
#-*- coding: utf-8 -*-

# Datenbank enthält:
# Title
# Artist
# Album
# TrackType
# Source (Volumio/Raumfeld)
# Should scrobble
# Scrobbled
# Timestamp

import json
import time
import urllib.request


class Track(object):
    def __init__(
            self,
            title,
            artist,
            album,
            tracktype='track',
            source='undefined',
            should_scrobble=True,
            scrobbled=False,
            idx=None,
            timestamp=time.time()):
        self.title = title
        self.artist = artist
        self.album = album

        self.tracktype = tracktype
        self.source = source
        self.should_scrobble = should_scrobble
        self.scrobbled = scrobbled
        self.idx = idx
        self.timestamp = timestamp

    def __eq__(self, other):
        return self.title == other.title and self.artist == other.artist and self.album == other.album

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return ('[IGN] ' if not self.should_scrobble else '') + (self.artist if self.artist else '') + " - " + self.title

    def get_dbvalues(self):
        return (
            self.title,
            self.artist,
            self.album,
            self.tracktype,
            self.source,
            self.should_scrobble,
            self.scrobbled
        )

    @staticmethod
    def from_dbvalues(dbvalue):
        idx, title, artist, album, _, _, _, _, timestamp = dbvalue
        return Track(title, artist, album, idx=idx, timestamp=timestamp)


class MediaPlayer(object):
    def __init__(self):
        pass

    def get_current_track(self):
        raise NotImplementedError


class VolumioPlayer(MediaPlayer):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_current_track(self):
        volumiostate = urllib.request.urlopen('http://{}:{}/api/v1/getState'.format(self.ip, self.port)).read()
        try:
            state = json.loads(volumiostate.decode('utf-8'))
            if state['status'] == 'stop':
                return None
            should_scrobble = state['trackType'] != 'webradio'
            return Track(
                state['title'],
                state['artist'],
                state['album'] if state['album'] else '',
                state['trackType'],
                source='volumio',
                should_scrobble=should_scrobble,
                scrobbled=False)
        except KeyError:
            print('KeyError')
            return None


class RaumfeldPlayer(MediaPlayer):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_current_track(self):
        # TODO: Auswerten, ob aktuell tatsächlich läuft
        raumfeldstate = urllib.request.urlopen('http://{}:{}/raumserver/controller/getRendererState'.format(self.ip, self.port)).read()
        try:
            state = json.loads(raumfeldstate.decode('utf-8'))['data'][0]['mediaItem']
            should_scrobble = state['name'] == 'Track'
            return Track(
                state['title'] if state['title'] else '',
                state['artist'] if state['artist'] else '',
                state['album'] if state['album'] else '',
                tracktype=state['name'] if state['name'] else '',
                source='raumfeld',
                should_scrobble=should_scrobble,
                scrobbled=False)
        except TypeError:
            return None


class MediaPlayerFactory(object):
    players = {
            'volumio': VolumioPlayer,
            'raumfeld': RaumfeldPlayer
        }

    @staticmethod
    def create(playertype, ip, port):
        return MediaPlayerFactory.players[playertype](ip, port)
