## Overview
This project consists of a semantic network of musical entities (songs, artists, genres, etc) with an API for retrieving and adding info. The included database was populated with data retrieved from Spotify's public web API. Originally, I developed this system as part of a broader [collaborative project](https://github.com/MIR-Directed-Research/intelligent-music-recommender).

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

And the following functions allow *retrieval* of information to the database

* `kr_api.get_all_music_entities()`: returns a list of names of all entities (songs, artists, and genres).
  * Used by UI modules to match user input with known entities.
* `kr_api.get_songs(artist)`: Retrieves list of song names for given artist name.
* `kr_api.get_artist_data(artist_name)`: Retrieves associated genres, node ID, and number of Spotify followers for given artist.
* `kr_api.get_song_data(song_name)`: Gets all songs that match given name, along with their artists.
  * List of all hits, each containing info about their node ID, artist (by name), duration in milliseconds, and popularity according to Spotify.
* `kr_api.get_related_entities(entity_name, rel_str)`: Finds all entities connected to the given entity by an edge with the given label `rel_str`.
  * This implements a key part of our KR system's functionality: **querying the semantic network!**
  * The given entity may be any of song, an artist, etc. The returned entity may or may not be the same type of entity.

## Testing
Run the tests from the project's root folder:
```
$ python run_tests.py
...
----------------------------------------------------------------------
Ran 32 tests in 0.943s

OK
```
