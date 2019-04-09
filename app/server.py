"""
This module defines the server's routing, including:
- a GET endpoint for getting the Muze interface
- a POST endpoint for Dialogflow webhook calls
- dispatchers and handlers for web socket events

The POST endpoint is specifically used for fullfilment of user requests,
made via the corresponding Dialogflow agent. See here for more info
(https://dialogflow.com/docs/fulfillment). Achieved with the
flask_assistant framework.

Execution:
    $ python app/server.py
"""

import dialogflow
from flask import Flask, render_template
from flask_assistant import Assistant, ask, tell
from flask_socketio import SocketIO
import logging
import random
import sys

sys.path.extend(['.', '../'])   # needed for import statement(s) below
from knowledge_base.api import KnowledgeBaseAPI

logging.getLogger('flask_assistant').setLevel(logging.DEBUG)
app = Flask(__name__)
assist = Assistant(app, route='/webhook', project_id='muze-2b5fa')
socket_io = SocketIO(app)
music_api = KnowledgeBaseAPI('knowledge_base/knowledge_base.db')

DIALOGFLOW_PROJECT_NAME = "muze-2b5fa"
# NOTE: this is a temporary measure; this app is not production-ready
CLIENT_SESSION_KEYS, MAX_CLIENT_SESSION = set(), 10

@app.route('/')
def get_player():
    return render_template("player.html")

@socket_io.on("start session")
def start_user_session():
    print(f"Received request from client to begin session..")

    session_key = None
    if len(CLIENT_SESSION_KEYS) > MAX_CLIENT_SESSION:
        print("Reached client session limit. Snubbing a client.")

    else:
        while session_key is None or session_key in CLIENT_SESSION_KEYS:
            session_key = random.randint(0,1000)
        CLIENT_SESSION_KEYS.add(session_key)
    socket_io.emit('session key', dict(session_key=session_key))

@socket_io.on("query")
def handle_user_query(data):
    if 'language_code' not in data:
        # Default to English
        data['language_code'] = 'en'

    print(f"Received query '{data['text']}' with session key: '{data['session_key']}'")

    df_client = dialogflow.SessionsClient()
    session = df_client.session_path(DIALOGFLOW_PROJECT_NAME, data['session_key'])
    query_input = dialogflow.types.QueryInput(
        text=dialogflow.types.TextInput(
            text=data['text'],
            language_code=data['language_code'],
        )
    )

    try:
        resp = df_client.detect_intent(session, query_input)
    except Exception as e:
        print(f"ERROR: Could not send query with Dialogflow agent: '{e}''")
        socket.emit(
            'message',
            dict(msg="Sorry I was thinking about something else, please try again.")
        )
        return

    msg_to_user, spotify_uri = None, None
    for msg in resp.query_result.fulfillment_messages:
        if msg.link_out_suggestion.destination_name == "Spotify":
            spotify_uri = msg.link_out_suggestion.uri
        elif hasattr(msg, 'text'):
            msg_to_user = str(msg.text.text[0])

    if spotify_uri is not None:
        print("Found song to play!")
        socket_io.emit(
            "play song",
            data=dict(
                spotify_uri=spotify_uri,
                msg=msg_to_user,
            ),
        )
    elif msg_to_user is not None:
        print("Could not find song to play!")
        socket_io.emit(
            'message',
            dict(msg=msg_to_user)
        )
    else:
        print("Could not find song to play!")
        socket_io.emit("not found")

@assist.action('Find Song')
def find_song(song, artist):
    """Fetches Spotify URI for specified song.

    Params:
        song (str): e.g. "thank u, next"
    """
    if song is None:
        return tell(f"Unfortunately, I could not understand the song name. Please try again.")

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
    if song is None:
        return tell(f"Unfortunately, I could not understand the song name. Please try again.")
    elif adjective is None:
        return tell(f"Unfortunately, I could not understand that phrase. Please try again.")

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
    socket_io.run(app, debug=True)
