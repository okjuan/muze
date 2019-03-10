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

@assist.action('About Song', mapping=dict(song_name='song'))
def get_song_info(song_name):
    """Fetches song info for specified song.

    Params:
        song_name (str): e.g. "thank u, next"
    """
    hits = music_api.get_song_data(song_name)
    if len(hits) == 0:
        return tell(f"Unfortunately, I couldn't find any info about {song_name}.")
    else:
        return ask(f"Do you mean the song {song_name} by {hits[0]['artist_name']}?")

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

    print(f"Songs more obscure than {song_name}: {[x['song_name'] for x in more_obscure_songs]}")
    print(f"Similar artists to {artist_name}: {similar_artists}")

    results = []
    for tmp_song_data in more_obscure_songs:
        if tmp_song_data['artist_name'] in similar_artists:
            results.append(tmp_song_data)

    if len(results) == 0:
        return tell(f"Unfortunately, I couldn't find any songs similar to but more obscure than {song_name}.")
    else:
        res_song_name = results[0]['song_name']
        res_artist_name = results[0]['artist_name']
        return tell(f"'{res_song_name}' by {res_artist_name} is similar but more obscure!")


if __name__ == '__main__':
    app.run(debug=True)
