"""
This module defines the server's routing, including:
- a GET endpoint for getting the Muze interface
- dispatchers and handlers for web socket events
- logic for using a Dialogflow to match user intents

Execution:
    $ python app/server.py
"""

import dialogflow
from flask import Flask, render_template
from flask_socketio import SocketIO
from google.oauth2 import service_account
import json
import logging
import os
import random
import sys

sys.path.extend(['.', '../'])   # needed for import statement(s) below
from knowledge_base.api import KnowledgeBaseAPI

app = Flask(__name__)
socket_io = SocketIO(app)
music_api = KnowledgeBaseAPI('knowledge_base/knowledge_base.db')

DIALOGFLOW_CREDS = None
DIALOGFLOW_PROJECT_ID = None
CLIENT_SESSION_KEYS, NEW_CLIENT_IDX, = [None for i in range(100)], 0
CLIENT_COUNT, MAX_CLIENT_SESSIONS = 0, 100

@app.route('/')
def get_player():
    return render_template("player.html")

@socket_io.on("start session")
def start_user_session():
    global NEW_CLIENT_IDX, CLIENT_COUNT
    print(f"Received request from client to begin session..")

    if CLIENT_COUNT >= MAX_CLIENT_SESSIONS:
        print("Reached client session limit. Replacing oldest client.")
        CLIENT_COUNT -= 1

    session_key = None
    while session_key is None or session_key in CLIENT_SESSION_KEYS:
        session_key = random.randint(0,1000)

    CLIENT_SESSION_KEYS[NEW_CLIENT_IDX] = session_key
    NEW_CLIENT_IDX = (NEW_CLIENT_IDX + 1) % MAX_CLIENT_SESSIONS
    CLIENT_COUNT += 1
    socket_io.emit('session key', dict(session_key=session_key))

@socket_io.on("query")
def handle_user_query(data):
    if 'language_code' not in data:
        # Default to English
        data['language_code'] = 'en'

    print(f"Received query '{data['text']}' with session key: '{data['session_key']}'")

    try:
        if DIALOGFLOW_CREDS is None:
            # Depends on env var GOOGLE_APPLICATION_CREDENTIALS
            df_client = dialogflow.SessionsClient()
        else:
            df_client = dialogflow.SessionsClient(credentials=DIALOGFLOW_CREDS)
        session = df_client.session_path(DIALOGFLOW_PROJECT_ID, data['session_key'])

    except Exception as e:
        print("ERROR: Can't talk to dialogflow without creds:", e)
        socket_io.emit("message", data=dict(msg="Sorry, I'm not feeling well. Please come back later."))
        return

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
        socket_io.emit(
            'message',
            dict(msg="Sorry I was thinking about something else, please try again.")
        )
        return

    msg_to_user, spotify_uri = None, None
    params = {x[0]:x[1] for x in resp.query_result.parameters.items()}
    if resp.query_result.intent.display_name == "Find Song":
        msg_to_user, spotify_uri = find_song(params["song"], params["artist"])

    elif resp.query_result.intent.display_name == "Find Slightly Different Song":
        msg_to_user, spotify_uri = get_finegrained_recommendation(params["song"], params["audio_feature_adjective"])

    if spotify_uri is not None:
        print("Found song to play!")
        socket_io.emit(
            "play song",
            data=dict(
                spotify_uri=spotify_uri,
                msg=msg_to_user,
            ),
        )

    else:
        print("Could not find song to play!")
        socket_io.emit(
            'message',
            dict(msg=msg_to_user)
        )

def find_song(song, artist):
    """Fetches Spotify URI for specified song.

    Params:
        song (str): e.g. "thank u, next"

    Returns:
        msg (str): describing result.
        spotify_uri (str).

    """
    if song is None or len(song) == 0:
        return f"Unfortunately, I could not understand the song name. Please try again.", None

    hits = music_api.get_song_data(song)
    if len(hits) == 0:
        return f"Unfortunately, I couldn't find {song}.", None
    else:
        if artist is not None and len(artist) > 0:
            for hit in hits:
                if hit['artist_name'] == artist:
                    return f"Found '{song}' by {artist}", hit['spotify_uri']
            return f"Unfortunately, I couldn't find {song} by {artist}.", None

        else:
            cur_artist = hits[0]['artist_name']
            spotify_uri = hits[0]['spotify_uri']
            return f"Found '{song}' by {cur_artist}", spotify_uri

def get_finegrained_recommendation(song, adjective, artist=None):
    """

    Params:
        song (str): e.g. "thank u, next".
        adjective (str): defined as Dialogflow entity Audio-Feature-Adjective.
            Should be a key in SONG_ADJECTIVES e.g. "bouncier", "more acoustic", etc.

    Returns:
        msg (str): describing result.
        spotify_uri (str).

    """
    if song is None or len(song) == 0:
        return "Unfortunately, I could not understand the song name. Please try again.", None
    elif adjective is None or len(adjective) == 0:
        return "Unfortunately, I could not understand that phrase. Please try again.", None

    hits = [
        hit for hit in music_api.get_song_data(song)
        if artist is None or hit["artist_name"].upper() == artist.upper()
    ]
    if len(hits) == 0:
        msg = f"Unfortunately, I could not find song '{song}'"
        if artist is None:
            return msg + ".", None
        else:
            return f"{msg} by '{artist}'", None

    elif len(hits) > 1:
        print(f"WARN: Found {len(hits)} hits for song '{song}'. Choosing one arbitrarily.")
    cur_song_data = hits[0]
    cur_artist = cur_song_data['artist_name']
    cur_song_id = cur_song_data["id"]

    # First, try to find song by same artist
    for candidate_song in music_api.get_songs_by_artist(cur_artist):
        if music_api.songs_are_related(candidate_song["id"], cur_song_id, rel_str=adjective):
            song_data = music_api.get_song_data(candidate_song["song_name"], candidate_song["id"])
            spotify_uri = song_data[0]['spotify_uri']
            return f"Found '{candidate_song['song_name']}' by {cur_artist}", spotify_uri

    # Otherwise, look for a song by another artist
    for related_artist in music_api.get_related_entities(cur_artist):
        for candidate_song in music_api.get_songs_by_artist(related_artist):
            if music_api.songs_are_related(candidate_song["id"], cur_song_id, rel_str=adjective):
                song_data = music_api.get_song_data(candidate_song["song_name"], candidate_song["id"])
                spotify_uri = song_data[0]['spotify_uri']
                return f"Found '{candidate_song['song_name']}' by {related_artist}", spotify_uri
    return f"Unfortunately, I could not find a song '{adjective}' than '{song}'.", None


if __name__ == '__main__':
    DIALOGFLOW_PROJECT_ID = os.environ.get("DIALOGFLOW_PROJECT_ID")
    # on Heroku, the port is an environment variable
    port = int(os.environ.get("PORT", 5000))
    dialogflow_key_file_raw_json = os.environ.get("DIALOGFLOW_KEY_FILE_RAW")

    if dialogflow_key_file_raw_json is not None:
        dialogflow_key_file_json = json.loads(dialogflow_key_file_raw_json)
        DIALOGFLOW_CREDS = service_account.Credentials.from_service_account_info(
            dialogflow_key_file_json
        )

    print("Running muze service on port:", port)
    socket_io.run(app, host="0.0.0.0", port=port)
