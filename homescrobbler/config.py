#!/usr/bin/python
#-*- coding: utf-8 -*-

import yaml
import homescrobbler.tracks as tracks


class Config(object):
    def __init__(self, filename):
        with open(filename, 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.BaseLoader)
        
        self.lastfm_api_key = config['lastfm']['api_key']
        self.lastfm_api_secret = config['lastfm']['api_secret']
        self.username = config['lastfm']['username']
        self.password_hash = config['lastfm']['password_hash']

        self.dbfile = config['db']['filename']
        
        self.players = []
        for device in config['devices']:
            for key in device.keys():
                player = tracks.MediaPlayerFactory.create(device[key]['type'], device[key]['ip'], device[key]['port'])
                self.players.append(player)
