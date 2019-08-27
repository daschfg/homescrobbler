#!/bin/sh

# Fetch request token
# Request authorization from user
#
# This is a very naiive helper script to register the scrobbler with a user account.
# Use at your own risk and feel free to improve.
# Call with your API key as first parameter or replace here.
# 
# Further information:
# https://www.last.fm/api/authentication
# https://www.last.fm/api/desktopauth

# Call with API key or replace here
api_key=$1

token_uri="http://ws.audioscrobbler.com/2.0/?method=auth.gettoken&api_key=$api_key&format=json"

# Fetch request token
result=$( curl $token_uri )
token=$( echo -ne $result | sed 's/.*:.*"\(\w*\)"}/\1/' )

auth_uri="https://last.fm/api/auth/?api_key=$api_key&token=$token"

# Open browser for user authentication
$BROWSER $auth_uri
