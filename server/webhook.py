"""
This module creates a POST endpoint for Dialogflow webhook calls.

Specifically, this endpoint is used for fullfilment of user requests,
made via the corresponding Dialogflow agent. See here for more info
(https://dialogflow.com/docs/fulfillment). Achieved with the
flask_assistant framework.

Execution:
    $ python server/webhook.py
"""

from flask import Flask
from flask_assistant import Assistant, ask, tell
import logging
import sys

sys.path.extend(['.', '../'])   # needed for import statement(s) below
from knowledge_base.api import KnowledgeBaseAPI

logging.getLogger('flask_assistant').setLevel(logging.DEBUG)
app = Flask(__name__)
assist = Assistant(app, route='/webhook')
music_api = KnowledgeBaseAPI('knowledge_base/knowledge_base.db')

@assist.action('Find Song')
def find_song(song, artist):
    """Fetches Spotify URI for specified song.

    Params:
        song (str): e.g. "thank u, next"
    """
    hits = music_api.get_song_data(song)
    if len(hits) == 0:
        return tell(f"Unfortunately, I couldn't find {song}.")
    else:
        if artist is not None:
            for hit in hits:
                if hit['artist_name'] == artist:
                    return tell(f"Found {song} by {artist}").link_out("Spotify", hit['spotify_uri'])
            return tell(f"Unfortunately, I couldn't find {song} by {artist}.")

        else:
            cur_artist = hits[0]['artist_name']
            spotify_uri = hits[0]['spotify_uri']
            return tell(f"Found {song} by {cur_artist}").link_out("Spotify", spotify_uri)

@assist.action('Get More Obscure Song', mapping=dict(song_name='song'))
def get_more_obscure_song(song_name):
    """Fetches a more obscure song than the given one and by a similar artist.

    Params:
        song_name (str): e.g. "thank u, next"
    """
    song_data = music_api.get_song_data(song_name)
    if len(song_data) == 0:
        return tell(f"Couldn't find song '{song_name}'")
    elif len(song_data) > 1:
        print(f"WARN: Found {len(song_data)} hits for song '{song_name}'. Choosing one arbitrarily.")

    artist_name = song_data[0]['artist_name']

    more_obscure_songs = music_api.get_less_popular_songs(song_name)
    similar_artists = music_api.get_related_entities(artist_name)

    results = []
    for tmp_song_data in more_obscure_songs:
        if tmp_song_data['artist_name'] in similar_artists:
            results.append(tmp_song_data)

    if len(results) == 0:
        return tell(f"Unfortunately, I couldn't find any songs similar to but more obscure than {song_name}.")
    else:
        res_song_name = results[0]['song_name']
        res_artist_name = results[0]['artist_name']
        spotify_uri = results[0]['spotify_uri']
        return tell(f"Found {res_song_name} by {res_artist_name}").link_out("Spotify", spotify_uri)

@assist.action('Find Slightly Different Song')
def get_finegrained_recommendation(song, audio_feature_adjective):
    res = music_api.get_song_data(song)
    if len(res) == 0:
        return tell(f"Unfortunately, I could not find song '{song}'.")
    else:
        print(f"WARN: Found {len(res)} hits for song '{song}'. Choosing one arbitrarily.")
        cur_song_data = res[0]
        cur_acousticness = res[0]['acousticness']

    if cur_acousticness is None:
        return tell(f"Unfortunately, I have no data regarding '{audio_feature_adjective}' of song '{song}'.")

    # TODO: get similar songs instead of song by same artist
    # similar_songs = music_api.get_related_entities(song)
    songs_by_same_artist = music_api.get_songs_by_artist(cur_song_data['artist_name'])

    if audio_feature_adjective == "more acoustic":
        compare = lambda x: x > cur_acousticness
    elif audio_feature_adjective == "less acoustic":
        compare = lambda x: x < cur_acousticness
    else:
        return tell(f"Unfortunately, I could not recognize '{audio_feature_adjective}' as an adjective.")

    for s in songs_by_same_artist:
        tmp_song_data = music_api.get_song_data(s)[0]
        tmp_acousticness = tmp_song_data['acousticness']
        if tmp_acousticness is not None and compare(tmp_acousticness):
            return tell(f"Found '{s}' by {tmp_song_data['artist_name']}")\
                .link_out("Spotify", tmp_song_data['spotify_uri'])
    return tell(f"Unfortunately, I could not find a song '{audio_feature_adjective}' than '{song}'.")


if __name__ == '__main__':
    app.run(debug=True)
