#!/usr/bin/python
#-*- coding: utf-8 -*-

import argparse
import os
import time
import homescrobbler.database as database
import homescrobbler.config as config
import homescrobbler.tracks as tracks
import homescrobbler.scrobbler as scrobbler


def log_music(cfg):
    with database.DBConnector(cfg.dbfile) as db:
        for player in cfg.players:
            track = player.get_current_track()
            if track and track not in db.get_last_tracks(4, track.source):
                db.add(track)
                timestamp = time.strftime('%d.%m.%y %H:%M:%S')
                print(timestamp + ': ' + str(track))


def scrobble(cfg):
    lastfm = scrobbler.LastFMConnector(
            api_key=cfg.lastfm_api_key,
            api_secret=cfg.lastfm_api_secret,
            username=cfg.username,
            password_hash=cfg.password_hash)
 
    with database.DBConnector(cfg.dbfile) as db:
        tracks = db.get_unscrobbled()
        for track in tracks:
            lastfm.scrobble(track)
            print('Scrobbled ', track)
            db.mark_scrobbled(track)


def main():
    parser = argparse.ArgumentParser(
            description='Log or scrobble music listened to',
        )

    parser.add_argument(
            'command',
            help='Subcommand to run',
            choices=['log', 'scrobble'],
        )
    parser.add_argument(
            '-c', '--config',
            help='Configfile',
            default=None
        )

    args = parser.parse_args()
    if args.config:
        print('Using', args.config, 'as config')
        configname = args.config
    elif os.path.isfile('docs/config.yml'):
        configname = 'docs/config.yml'
    else:
        configname = 'docs/config_default.yml'

    cfg = config.Config(configname)
    if args.command == 'log':
        log_music(cfg)
    elif args.command == 'scrobble':
        scrobble(cfg)

    
if __name__ == '__main__':
   main() 
