#!/usr/bin/python
#-*- coding: utf-8 -*-

import database
import tracks
import time

from config import *


if __name__ == '__main__':
    track1 = tracks.RaumfeldTrack.from_currently_playing(raumfeld_address)
    track2 = tracks.VolumioTrack.from_currently_playing(volumio_address)

    tracks = []
    if track1:
        tracks.append(track1)
    if track2:
        tracks.append(track2)

    with database.DBConnector(dbfile) as db:
        for track in tracks:
            last_tracks = db.get_last_tracks(4, track.source)
            if track not in last_tracks:
                db.add(track)
                timestamp = time.strftime('%e.%d.%y %H:%M:%S')
                print(timestamp, ': ', track)
