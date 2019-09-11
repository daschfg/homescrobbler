#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import homescrobbler.tracks as tracks


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
                should_scrobble BOOLEAN,
                scrobbled BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
        self.cursor.execute(create_cmd)

    def add(self, track):
        assert isinstance(track, tracks.Track)
        entry_cmd = """
            INSERT INTO playlog (title, artist, album, tracktype, source, should_scrobble, scrobbled)
            VALUES (?, ?, ?, ?, ?, ?, ?);"""
        self.cursor.execute(entry_cmd, track.get_dbvalues())
        self.connection.commit()

    def get_last_entries(self, n=1, source=None):
        lastentry_cmd = """
        SELECT * FROM playlog
        ORDER BY id DESC LIMIT ?;
        """
        lastentry_cmd_filtered = """
        SELECT * FROM playlog
        WHERE source = ? ORDER BY id DESC LIMIT ?;
        """
        if source is None:
            self.cursor.execute(lastentry_cmd, (n,))
        else:
            self.cursor.execute(lastentry_cmd_filtered, (n, source))
        return self.cursor.fetchall()

    def get_last_tracks(self, n=1, source=None):
        return [i for i in map(tracks.Track.from_dbvalues,
                               self.get_last_entries(source, n))]

    def is_existent(self):
        existent_cmd = """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='playlog';
        """
        self.cursor.execute(existent_cmd)
        return len(self.cursor.fetchall()) == 1

    def get_unscrobbled(self):
        unscrobbled_cmd = """
        SELECT * FROM playlog
        WHERE should_scrobble AND NOT scrobbled;
        """
        self.cursor.execute(unscrobbled_cmd)
        return [i for i in map(tracks.Track.from_dbvalues,
                               self.cursor.fetchall())]

    def mark_scrobbled(self, track):
        if not track.idx:
            raise ValueError('Not in DB')
        set_scrobbled_cmd = """
        UPDATE playlog
        SET scrobbled = 1
        WHERE id = ?;
        """
        self.cursor.execute(set_scrobbled_cmd, (track.idx,))
        self.connection.commit()
