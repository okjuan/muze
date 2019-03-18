## Overview
This project consists of a semantic network of musical entities (songs, artists, genres, etc) with an API for retrieving and adding info. The included database was populated with data retrieved from Spotify's public web API. Originally, I developed this system as part of a broader [collaborative project](https://github.com/MIR-Directed-Research/intelligent-music-recommender).

Additionally, a server endpoint for use by a Dialogflow agent is under construction. Specifically, the endpoint is a [webhook for fulfillment](https://dialogflow.com/docs/fulfillment) of a user request as handled by Dialogflow.

## Setup
### Prerequisites
* [SQLite3](https://www.sqlite.org/download.html)
* [Python](https://www.python.org/downloads/) 3.5 or higher

### Dependencies
Whether or not you use a virtual environment:
```
pip install -r requirements.txt
```

## API
In general, the Knowledge Representation (KR) API exposes a collection of functions that encapsulate all SQL queries and logic relating to managing the database; through the KR API, callers may retrieve from and add information to the database. The following functions allow *addition* of information to the database through an instance `kr_api` of the `KnowledgeBaseAPI` class:

* `kr_api.add_artist()`: Inserts given values into two tables: `artists` and `nodes`.
  * Given artist is only added if they are not already in the database.
  * Given artist is either added to both tables or neither.
* `kr_api.add_song()`: Inserts given values into two tables: songs and nodes.
  * Given song is either added to both tables or neither.
  * Given artist is not ambiguous (only matches one 'artist' entry in nodes table).
  * Given tuple (song, artist) is only added if it does not already exist in database.
* `kr_api.add_genre()`: Adds given value into two tables: genres and nodes.
  * Given genre is eiter added to both tables or neither.
  * Given genre is only added if not already in the database.
* `kr_api._add_node()`: Adds given entity to the nodes table.
  * Intended for "private" use only, as indicated by the leading underscore in the function's name [8]
  * Used by all other `add_` functions.
* `kr_api.connect_entities(source_node_name, dest_node_name, rel_str, score)`: Insert into `edges` table.
  * Creates an edge in semantic network with given label `rev_str` (e.g. "similar to", "of genre") and score

Various functions allow *retrieval* of information to the database; some of them are described below:

* `kr_api.get_songs(artist)`: Retrieves list of song names for given artist name.
* `kr_api.get_artist_data(artist_name)`: Retrieves associated genres, node ID, and number of Spotify followers for given artist.
* `kr_api.get_song_data(song_name)`: Gets all songs that match given name, along with their artists.
  * List of all hits, each containing info about their node ID, artist (by name), duration in milliseconds, and popularity according to Spotify.
* `kr_api.get_related_entities(entity_name, rel_str)`: Finds all entities connected to the given entity by an edge with the given label `rel_str`.
  * This implements a key part of our KR system's functionality: **querying the semantic network!**
  * The given entity may be any of song, an artist, etc. The returned entity may or may not be the same type of entity.
* `kr_api.get_less_popular_songs(song_name)`: Finds all songs with lower Spotify popularity score

## Testing
### Demoing the Application
This section contains instructions for testing this serverside app in connection with its corresponding Dialogflow agent. Installing [ngrok](https://ngrok.com/) is an easy way to run the service the locally and make it publicly available so that it can communicate with the Dialogflow agent.

* Run the serverside app: `python server/webhook.py`
* Run `./ngrok http 5000` to connect local server to relay server, making it publicly available
* Copy HTTPS URL on the screen (e.g. `https://f313aea9.ngrok.io`)
* In Dialogflow console, in Fulfillment tab, enable the Webhook option and paste the ngrok HTTPS url with `/webhook` appended to it (e.g. `https://f313aea9.ngrok.io/webhook`)
* Open `player.html` and enter "Who is the song If Only by?", the UI should play the song _If Only_ by Raveena.
  * Make sure to get fresh access tokens for both [Spotify](https://developer.spotify.com/documentation/web-playback-sdk/quick-start/#authenticating-with-spotify) and Dialogflow (with gcloud CLI, as described [here](https://dialogflow.com/docs/reference/v2-auth-setup)), and paste them in `client/player.js` and `client/script.js` respectively

### Unit Tests
Run the tests from the project's root folder:
```
$ python run_tests.py
...
----------------------------------------------------------------------
Ran 32 tests in 0.943s

OK
```
