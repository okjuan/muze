"""
Contains two distinct functions for populating the test database with one of:
- Arbitrary data
- Spotify data
"""

import os
import pprint
import subprocess
import sys

sys.path.append('../')  # if running this script from 'scripts/' directory
sys.path.append('.')  # if running this script from project root
sys.path.append('./scripts')  # if running this script from project root
from knowledge_base.api import KnowledgeBaseAPI

pp = pprint.PrettyPrinter(
    indent=2,
    depth=2,  # hide items nested past 3 levels
    compact=True,  # fit as many items into a single line as possible
)

TEST_DB_NAME = "test.db"
SCHEMA_FILE_NAME = "schema.sql"
TEST_DATA_FILE_NAME = "test_data.sql"
SPOTIFY_COUNTRY_ISO = "CA"


def exec_sql_script(db_path, path_to_sql_file, DB_name: str = None):
    """Equivalent to running the following command in terminal:
        $ sqlite3 path_to_test_db_file < schema_file.sql

    Params:
        path_prefix (string): specifies directory to test db (creating it if dne).
        path_to_sql_file (string): path to sql script.
    """
    with open(path_to_sql_file) as f:
        subprocess.run(["sqlite3", db_path], stdin=f)

def create_and_populate_db(path: str = None):
    "Creates DB and fills it with test data."
    db_path = create_db(path)
    _, scripts_path_prefix = _get_path_prefixes()
    exec_sql_script(db_path, scripts_path_prefix + TEST_DATA_FILE_NAME)
    return db_path

def create_db(path: str = None):
    """Creates and fills sqlite database, saving .db file to 'tests/'
   directory, unless another path is specified.

   Tries to find SQL scripts depending on where this module is invoked from.

   Returns:
       (string): (relative) path to newly created .db file.
   """
    test_db_path_prefix, scripts_path_prefix = _get_path_prefixes()
    db_path = path or (test_db_path_prefix + TEST_DB_NAME)

    exec_sql_script(db_path, scripts_path_prefix + SCHEMA_FILE_NAME)
    return db_path

def _get_path_prefixes():
    "Used for adjusting path based on where the script is run from."
    cur_dir = os.getcwd().split("/")[-1]

    # From tests folder in project root dir
    if cur_dir == "tests":
        test_db_path_prefix = ""
        scripts_path_prefix = "../scripts/"

    # From scripts folder in project root dir
    elif cur_dir == "scripts":
        test_db_path_prefix = "../tests/"
        scripts_path_prefix = ""

    # From project root dir
    else:
        test_db_path_prefix = "tests/"
        scripts_path_prefix = "scripts/"
    return test_db_path_prefix, scripts_path_prefix

def remove_db():
    "Returns True if command succeeded, False otherwise."
    test_db_path, _ = _get_path_prefixes()
    return subprocess.run(["rm", test_db_path + TEST_DB_NAME]).returncode == 0

def _get_artist_data(spotify, artists):
    """Fetches data for each given artist.
    Params:
        spotify (SpotifyClient): for making requests to Spotify web API.
        artists (iterable): each element is an artist name.
            (e.g. list of strings, file with artist names on each line)

    Returns:
        artist_data (dict): key is artist name, value is a dict containing artist metadata.
            e.g. {
                "Justin Bieber": {
                    id=1uNFoZAHBGtllmzznpCI3s,
                    num_followers=25683438,
                    genres=["canadian pop", "dance pop", "pop", "post-teen pop"]
                }
                ...
            }
    """
    artist_data = dict()
    for tmp_artist_name in artists:
        tmp_artist_name = tmp_artist_name.strip()
        data = spotify.get_artist_data(tmp_artist_name)
        if data is not None:
            artist_data[tmp_artist_name] = data
    return artist_data

def _get_artist_metadata(spotify, artist_names):
    """Fetches metadata for each given artist.

    Returns:
        full_artist_metadata (dict): key is artist name, val is dict with:
            Spotify id, genres, number of Spotify followers, & related artists.

    e.g. {
        "Raveena": {
            'id': '2kQnsbKnIiMahOetwlfcaS',
            'genres': ['indie r&b'],
            'num_followers': 19191,
            'related_artists': {
                'Alextbh': {
                    'id': '0kXDB5aeESWj5BD9TCLkMu',
                    'genres': ['indie r&b', 'malaysian indie'],
                    'num_followers': 19517
                },
                ...
            },
        }
        ...

    """
    artist_summaries = _get_artist_data(spotify, artist_names)
    full_artist_metadata = dict()
    for artist, artist_summary in artist_summaries.items():
        full_artist_metadata[artist] = dict(
            id=artist_summary["id"],
            num_followers=artist_summary["num_followers"],
            genres=artist_summary["genres"],
            related_artists=spotify.get_related_artists(artist_summary["id"]),
        )
    return full_artist_metadata

def create_and_populate_db_with_spotify(spotify_client_id, spotify_secret_key, artists, path=None):
    """Pulls data from Spotify and adds it to knowledge base through its API.

    Params:
        spotify_client_id (str) e.g. "".
        spotify_secret_key (str) e.g. "".
        artists (iterable) each element is an artist name (str).
            For example, might be stdin, or open file, or list.
        path (str): relative path e.g. "knowledge_base.db".

    Returns:
        path_to_db (str): relative path to newly created db e.g. "knowledge_base/knowledge_base.db"
    """
    from utils.spotify_client import SpotifyClient
    path_to_db = create_db(path=path)
    spotify = SpotifyClient(spotify_client_id, spotify_secret_key)

    artist_metadata = _get_artist_metadata(spotify, artists)
    kb_api = KnowledgeBaseAPI(path_to_db)
    for artist_name, artist_info in artist_metadata.items():
        kb_api.add_artist(artist_name, artist_info["genres"], artist_info["num_followers"])

        songs = spotify.get_top_songs(artist_info['id'], SPOTIFY_COUNTRY_ISO)
        all_audio_features = spotify.get_audio_features([song_info['id'] for _, song_info in songs.items()])
        for song_name, song_info in songs.items():
            cur_audio_features = all_audio_features[song_info['id']]
            cur_mode = cur_audio_features['mode']
            cur_audio_features['mode'] = 'major' if cur_mode == 1 else 'minor'

            kb_api.add_song(
                song_name,
                artist_name,
                song_info["popularity"],
                song_info["duration_ms"],
                song_info["uri"],
                cur_audio_features,
            )

        for rel_artist_name, rel_artist_info in artist_info["related_artists"].items():
            kb_api.add_artist(rel_artist_name, rel_artist_info["genres"], rel_artist_info["num_followers"])
            kb_api.connect_entities(artist_name, rel_artist_name, "similar to", 100)
            kb_api.connect_entities(rel_artist_name, artist_name, "similar to", 100)
    return path_to_db
