#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Scrobble alle bislang nicht gescrobbelten Tracks der Lib
"""

import pylast
import logmusic
import sqlite3
import time
from datetime import datetime
from datetime import timezone
from dateutil import parser
from dateutil import tz

from config import *


if __name__ == '__main__':
    network = logmusic.LastFMConnector(
            api_key=API_KEY,
            api_secret=API_SECRET,
            username=lastfm_username,
            password_hash=lastfm_password_hash)
 
    with logmusic.DBConnector(dbfile) as db:
        tracks = db.get_unscrobbled()
        for track in tracks:
            #print(': ', track)
            network.scrobble(track)
            print('Scrobbled ', track)
            db.mark_scrobbled(track)
