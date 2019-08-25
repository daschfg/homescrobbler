#!/usr/bin/python
#-*- coding: utf-8 -*-

# Enthält:
# Title
# Artist
# Album
# TrackType
# Source (Volumio/Raumfeld)
# Timestamp

from datetime import datetime
import json
import pylast
from pylast import LastFMNetwork
import sqlite3
import time
import urllib.request

from config import *


class Track(object):
    def __init__(self, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album

        self.tracktype = 'track'
        self.source = 'undefined'

    def __eq__(self, other):
        return self.title == other.title and self.artist == other.artist and self.album == other.album

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return (self.artist if self.artist else '') + " - " + self.title

    def get_dbvalues(self):
        return (
            track.title,
            track.artist,
            track.album,
            track.tracktype,
            track.source
        )

    @staticmethod
    def from_dbvalues(dbvalue):
        title, artist, album = dbvalue[1:4]
        return Track(title, artist, album)


class VolumioTrack(Track):
    def __init__(self, title, artist, album, tracktype):
        Track.__init__(self, title, artist, album)
        self.tracktype = tracktype
        self.source = 'volumio'

    @staticmethod
    def from_currently_playing(source):
        volumiostate = urllib.request.urlopen('http://{}:{}/api/v1/getState'.format(source[0], source[1])).read()
        state = json.loads(volumiostate)
        return VolumioTrack(
            state['title'],
            state['artist'],
            state['album'] if state['album'] else '',
            state['trackType'])


class RaumfeldTrack(Track):
    def __init__(self, title, artist, album, tracktype):
        Track.__init__(self, title, artist, album)
        self.tracktype = tracktype
        self.source = 'raumfeld'

    @staticmethod
    def from_currently_playing(source):
        raumfeldstate = urllib.request.urlopen('http://{}:{}/raumserver/controller/getRendererState'.format(source[0], source[1])).read()
        try:
            state = json.loads(raumfeldstate)['data'][0]['mediaItem']
            return RaumfeldTrack(
                state['title'] if state['title'] else '',
                state['artist'] if state['artist'] else '',
                state['album'] if state['album'] else '',
                state['name'] if state['name'] else '')
        except TypeError:
            return None


class DBConnector(object):
    def __init__(self, filename):
        self.connection = None
        self.cursor = None
        self.filename = filename

    def __enter__(self):
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
        if not self.is_existent():
            self.create()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def create(self):
        create_cmd = """
            CREATE TABLE playlog (
                id INTEGER PRIMARY KEY,
                title VARCHAR(128),
                artist VARCHAR(128),
                album VARCHAR(128),
                tracktype VARCHAR(40),
                source VARCHAR(20),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
        self.cursor.execute(create_cmd)

    def add(self, track):
        assert isinstance(track, Track)
        entry_cmd = """
            INSERT INTO playlog (title, artist, album, tracktype, source)
            VALUES (?, ?, ?, ?, ?);"""
        self.cursor.execute(entry_cmd, track.get_dbvalues())
        self.connection.commit()

    def get_last_entries(self, n=1, source=None):
        lastentry_cmd = """
        SELECT * FROM playlog ORDER BY id DESC LIMIT ?;
        """
        lastentry_cmd_filtered = """
        SELECT * FROM playlog WHERE source = ? ORDER BY id DESC LIMIT ?;
        """
        if source is None:
            self.cursor.execute(lastentry_cmd, (n,))
        else:
            self.cursor.execute(lastentry_cmd_filtered, (n, source))
        return self.cursor.fetchall()

    def get_last_tracks(self, n=1, source=None):
        return [i for i in map(Track.from_dbvalues, self.get_last_entries(source, n))]

    def is_existent(self):
        existent_cmd = """
        SELECT name FROM sqlite_master WHERE type='table' AND name='playlog';
        """
        self.cursor.execute(existent_cmd)
        return len(self.cursor.fetchall()) == 1


class LastFMConnector(LastFMNetwork):
    def __init__(self, api_key, api_secret, username, password_hash):
        LastFMNetwork.__init__(
                self,
                api_key=api_key,
                api_secret=api_secret,
                username=username,
                password_hash=password_hash)

    def scrobble(self, track):
        LastFMNetwork.scrobble(self, track.artist, track.title, time.time(), track.album)


if __name__ == '__main__':
    #uri = "http://ws.audioscrobbler.com/2.0/?method=auth.gettoken&api_key={}&format=json".format(API_KEY)
    #result = urllib.request.urlopen(uri).read()
    #print(result)

    network = LastFMConnector(
            api_key=API_KEY,
            api_secret=API_SECRET,
            username=lastfm_username,
            password_hash=lastfm_password_hash)

    #track = VolumioTrack.from_currently_playing(volumio_address)
    #print(track)
    #network.scrobble(track.artist, track.title, datetime.utcnow(), track.album)
    #network.scrobble(track)

    #track1 = RaumfeldTrack.from_currently_playing(raumfeld_address)
    track1 = None
    track2 = VolumioTrack.from_currently_playing(volumio_address)

    tracks = []
    if track1:
        tracks.append(track1)
    if track2:
        tracks.append(track2)

    with DBConnector(dbfile) as db:
        for track in tracks:
            last_tracks = db.get_last_tracks(4, track.source)
            if track not in last_tracks:
                db.add(track)
                network.scrobble(track)
                timestamp = time.strftime('%e.%d.%y %H:%M:%S')
                print(timestamp, ': ', track)
