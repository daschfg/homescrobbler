#!/usr/bin/python
#-*- coding: utf-8 -*-

import database
import os
import tracks
import time
import config


if __name__ == '__main__':
    if os.path.isfile('./config.yml'):
        configname = 'config.yml'
    else:
        configname = 'config_default.yml'

    cfg = config.Config(configname)
    players = cfg.players

    with database.DBConnector(cfg.dbfile) as db:
        for player in players:
            track = player.get_current_track()
            if track and track not in db.get_last_tracks(4, track.source):
                db.add(track)
                timestamp = time.strftime('%d.%m.%y %H:%M:%S')
                print(timestamp + ': ' + str(track))
