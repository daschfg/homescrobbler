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
    def __init__(self, title, artist, album, should_scrobble=True, scrobbled=False, idx=None, timestamp=time.time()):
        self.title = title
        self.artist = artist
        self.album = album

        self.tracktype = 'track'
        self.source = 'undefined'
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


class VolumioTrack(Track):
    def __init__(self, title, artist, album, tracktype, should_scrobble=True, scrobbled=False):
        Track.__init__(self, title, artist, album, should_scrobble, scrobbled)
        self.tracktype = tracktype
        self.source = 'volumio'

    @staticmethod
    def from_currently_playing(source):
        volumiostate = urllib.request.urlopen('http://{}:{}/api/v1/getState'.format(source[0], source[1])).read()
        try:
            state = json.loads(volumiostate)
            if state['status'] == 'stop':
                return None
            should_scrobble = state['trackType'] != 'webradio'
            return VolumioTrack(
                state['title'],
                state['artist'],
                state['album'] if state['album'] else '',
                state['trackType'],
                should_scrobble=should_scrobble)
        except KeyError:
            return None


class RaumfeldTrack(Track):
    def __init__(self, title, artist, album, tracktype, should_scrobble=True, scrobbled=False):
        Track.__init__(self, title, artist, album, should_scrobble, scrobbled)
        self.tracktype = tracktype
        self.source = 'raumfeld'

    @staticmethod
    def from_currently_playing(source):
        raumfeldstate = urllib.request.urlopen('http://{}:{}/raumserver/controller/getRendererState'.format(source[0], source[1])).read()
        try:
            state = json.loads(raumfeldstate)['data'][0]['mediaItem']
            should_scrobble = state['name'] == 'Track'
            return RaumfeldTrack(
                state['title'] if state['title'] else '',
                state['artist'] if state['artist'] else '',
                state['album'] if state['album'] else '',
                state['name'] if state['name'] else '',
                should_scrobble=should_scrobble)
        except TypeError:
            return None
