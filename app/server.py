"""
This module defines the server's routing, including:
- a GET endpoint for getting the Muze interface
- dispatchers and handlers for web socket events
- logic for using a Dialogflow to match user intents

Execution:
    $ python app/server.py
"""

from flask import Flask, render_template
from flask_socketio import SocketIO
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

    rel_artists = music_api.get_related_entities(cur_artist) + [cur_artist]
    random.shuffle(rel_artists)
    for related_artist in rel_artists:
        songs_by_rel_artist = music_api.get_songs_by_artist(related_artist)
        random.shuffle(songs_by_rel_artist)
        for candidate_song in songs_by_rel_artist:
            if music_api.songs_are_related(candidate_song["id"], cur_song_id, rel_str=adjective):
                song_data = music_api.get_song_data(candidate_song["song_name"], candidate_song["id"])
                spotify_uri = song_data[0]['spotify_uri']
                return f"Found '{candidate_song['song_name']}' by {related_artist}", spotify_uri
    return f"Unfortunately, I could not find a song '{adjective}' than '{song}'.", None

@socket_io.on("get random song")
def get_random_song():
    socket_io.emit(
        "play song",
        data=dict(spotify_uri=music_api.get_random_song()),
    )


if __name__ == '__main__':
    # on Heroku, the port is an environment variable
    port = int(os.environ.get("PORT", 5000))
    print("Running muze service on port:", port)
    socket_io.run(app, host="0.0.0.0", port=port)
