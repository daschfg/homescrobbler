#!/usr/bin/python
#-*- coding: utf-8 -*-

import database
import tracks
import time
from config import *


if __name__ == '__main__':
    players = [
            tracks.VolumioPlayer(volumio_address[0], volumio_address[1]),
            tracks.RaumfeldPlayer(raumfeld_address[0], raumfeld_address[1])
            ]

    with database.DBConnector(dbfile) as db:
        for player in players:
            track = player.get_current_track()
            if track and track not in db.get_last_tracks(4, track.source):
                db.add(track)
                timestamp = time.strftime('%d.%m.%y %H:%M:%S')
                print(timestamp + ': ' + str(track))
