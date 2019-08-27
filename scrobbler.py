#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Scrobble alle bislang nicht gescrobbelten Tracks der Lib
"""

import database
from pylast import LastFMNetwork
import logmusic
import time
from datetime import datetime
from datetime import timezone
from dateutil import parser
from dateutil import tz

from config import *


class LastFMConnector(LastFMNetwork):
    def __init__(self, api_key, api_secret, username, password_hash):
        LastFMNetwork.__init__(
                self,
                api_key=api_key,
                api_secret=api_secret,
                username=username,
                password_hash=password_hash)

    def scrobble(self, track):
        if track.timestamp:
            timestamp = parser.parse(track.timestamp).replace(tzinfo=timezone.utc)
            timestamp = time.mktime(timestamp.astimezone(tz.tzlocal()).timetuple())
        else:
            timestamp = time.time()
        LastFMNetwork.scrobble(self, track.artist, track.title, timestamp, track.album)


if __name__ == '__main__':
    lastfm = LastFMConnector(
            api_key=API_KEY,
            api_secret=API_SECRET,
            username=lastfm_username,
            password_hash=lastfm_password_hash)
 
    with database.DBConnector(dbfile) as db:
        tracks = db.get_unscrobbled()
        for track in tracks:
            lastfm.scrobble(track)
            print('Scrobbled ', track)
            db.mark_scrobbled(track)
