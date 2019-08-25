#!/usr/bin/python
#-*- coding: utf-8 -*-

# Enthält:
# Title
# Artist
# Album
# TrackType
# Source (Volumio/Raumfeld)
# Timestamp

import json
import sqlite3
import time
import urllib.request

logfile="/home/daniel/musiclog.db"

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
        return self.artist + " - " + self.title

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


class DBConnector(object):
    def __init__(self, filename):
        self.connection = None
        self.cursor = None
        self.filename = filename

    def __enter__(self):
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
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

    def get_last_entries(self, n=1):
        lastentry_cmd = """SELECT * FROM playlog ORDER BY id DESC LIMIT ?;"""
        self.cursor.execute(lastentry_cmd, (n,))
        return self.cursor.fetchall()

    def get_last_tracks(self, n=1):
        return [i for i in map(Track.from_dbvalues, self.get_last_entries(n))]


if __name__ == '__main__':
    volumiostate = urllib.request.urlopen('http://192.168.2.104:3000/api/v1/getState').read()
    state = json.loads(volumiostate)
    #print(json.dumps(state, indent=4))

    track = VolumioTrack(
            state['title'],
            state['artist'],
            state['album'] if state['album'] else '',
            state['trackType'])

    #print(json.dumps(entry, indent=4))
    with DBConnector(logfile) as db:
        last_tracks = db.get_last_tracks(4)
        if track not in last_tracks:
            db.add(track)
            timestamp = time.strftime('%e.%d.%y %H:%M:%S')
            print(timestamp, ': ', track)
