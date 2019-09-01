# homescrobbler

**homescrobbler** is a tool for monitoring media players in a network to log audio files they play and submit them to a Last.FM-useraccount.

Currently supported are devices running

- [node-raumserver](https://github.com/ChriD/node-raumserver) and
- [Volumio](https://volumio.org/)

Logged data is stored in a sqlite3-database.

## Configuration

Configuration is stored in a YAML-file (docs/config_default.yml).

## Usage

	# Log currently playing track
	python -m homescrobbler log
	
	# List all unsubmitted tracks
	python -m homescrobbler list
	
	# Submit all new tracks
	python -m homescrobbler scrobble

## Submitting to Last.FM

To submit your logged data, you need a valid API-key from Last.FM and you need to authenticate this API-key with the useraccount.
This API-key and -secret together with the username and MD5-hashed password should be stored in the config file (docs/config_default.yml).

For further information:
[https://www.last.fm/api/authentication](https://www.last.fm/api/authentication)
[https://www.last.fm/api/desktopauth](https://www.last.fm/api/desktopauth)
