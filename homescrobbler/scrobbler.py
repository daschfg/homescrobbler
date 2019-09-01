#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Scrobble alle bislang nicht gescrobbelten Tracks der Lib
"""

from pylast import LastFMNetwork
import time
#from datetime import datetime
from datetime import timezone
from dateutil import parser
from dateutil import tz


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
