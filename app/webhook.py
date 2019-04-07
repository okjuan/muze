"""
This module creates a POST endpoint for Dialogflow webhook calls.

Specifically, this endpoint is used for fullfilment of user requests,
made via the corresponding Dialogflow agent. See here for more info
(https://dialogflow.com/docs/fulfillment). Achieved with the
flask_assistant framework.

Execution:
    $ python server/webhook.py
"""

from flask import Flask, render_template
from flask_assistant import Assistant, ask, tell
import logging
import sys

sys.path.extend(['.', '../'])   # needed for import statement(s) below
from knowledge_base.api import KnowledgeBaseAPI

logging.getLogger('flask_assistant').setLevel(logging.DEBUG)
app = Flask(__name__)
assist = Assistant(app, route='/webhook', project_id='muze-2b5fa')
music_api = KnowledgeBaseAPI('knowledge_base/knowledge_base.db')


@app.route('/')
def get_player():
    return render_template("player.html")

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

@assist.action('Find Slightly Different Song', mapping=dict(adjective='audio_feature_adjective'))
def get_finegrained_recommendation(song, adjective):
    """

    Params:
        song (str): e.g. "thank u, next".
        adjective (str): defined as Dialogflow entity Audio-Feature-Adjective.
            Should be a key in SONG_ADJECTIVES e.g. "bouncier", "more acoustic", etc.

    """
    hits = music_api.get_song_data(song)
    if len(hits) == 0:
        return tell(f"Unfortunately, I could not find song '{song}'.")
    elif len(hits) > 1:
        print(f"WARN: Found {len(hits)} hits for song '{song}'. Choosing one arbitrarily.")
    cur_song_data = hits[0]
    cur_artist = cur_song_data['artist_name']

    # First, try to find song by same artist
    for candidate_song in music_api.get_songs_by_artist(cur_artist):
        if music_api.songs_are_related(candidate_song, song, rel_str=adjective):
            return tell(
                f"Found '{candidate_song}' by {cur_artist}"
            ).link_out(
                "Spotify",
                music_api.get_song_data(candidate_song)[0]['spotify_uri'],
            )

    # Otherwise, look for a song by another artist
    for related_artist in music_api.get_related_entities(cur_artist):
        for candidate_song in music_api.get_songs_by_artist(related_artist):
            if music_api.songs_are_related(candidate_song, song, rel_str=adjective):
                return tell(
                    f"Found '{candidate_song}' by {related_artist}"
                ).link_out(
                    "Spotify",
                    music_api.get_song_data(candidate_song)[0]['spotify_uri'],
                )
    return tell(f"Unfortunately, I could not find a song '{adjective}' than '{song}'.")


if __name__ == '__main__':
    app.run(debug=True)
