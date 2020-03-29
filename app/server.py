"""
This module defines the server's routing, including:
- a GET endpoint for getting the Muze interface
- dispatchers and handlers for web socket events

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

@socket_io.on("get recommendation")
def handle_get_recommendation(data):
    song, adjective = data.get('song'), data.get('adjective')
    if adjective is None:
        print(f"Received request for song similar to '{song}'")
        spotify_uri = get_similar_song(song)
    else:
        print(f"Received '{adjective}' request for song '{song}'")
        spotify_uri = get_finegrained_recommendation(song, adjective)

    if spotify_uri is None:
        msg = f"Could not get recommendation for song '{song}'"
        print(msg)
        socket_io.emit('msg', msg)
    else:
        print(f"Found recommendation for song '{song}'")
        socket_io.emit('play song', data=dict(spotify_uri=spotify_uri))

def get_similar_song(song_name):
    """Encapsulates interaction with music API for getting a recommendation.

    Params: song_name (str): e.g. 'No One', 'needy', etc.
    Returns: (str): a spotify URI or None if failure.
    """
    cur_song_data = music_api.get_song_data(song_name)
    if cur_song_data == []:
        print(f"ERR: Could not find song '{song_name}'.")
        return None
    elif len(cur_song_data) > 1:
        print(f"WARN: Found {len(cur_song_data)} hits for song '{song_name}'. Choosing one arbitrarily.")
    cur_song_data = cur_song_data[0]

    recommended_songs = music_api.get_related_entities(song_name)
    if recommended_songs == []:
        cur_artist = cur_song_data['artist_name']
        related_artists = music_api.get_related_entities(cur_artist) + [cur_artist]
        if len(related_artists) > 0:
            # TODO: use music api IDs (as soon as other get_related_entities called above also returns them)
            recommended_songs = [x['song_name']
                for x in music_api.get_songs_by_artist(
                    related_artists[random.randint(0, len(related_artists)-1)]
                )
            ]

    if recommended_songs == []:
        print(f"ERR: Couldn't find recommendations for song: '{song_name}'")
        return None
    elif len(recommended_songs) > 1:
        print(f"WARN: Found {len(recommended_songs)} hits for song '{song_name}'. Choosing one arbitrarily.")

    recommended_song = recommended_songs[random.randint(0, len(recommended_songs)-1)]
    hits = music_api.get_song_data(song_name=recommended_song)
    if hits == []:
        print(f"ERR: Couldn't find song info for: '{song_name}'")
        return None
    elif len(hits) > 1:
        print(f"WARN: Found {len(hits)} hits for song '{song_name}'. Choosing one arbitrarily.")
    return hits[0]['spotify_uri']

def get_finegrained_recommendation(song, adjective, artist=None):
    """

    Params:
        song (str): e.g. "thank u, next".
        adjective (str): should be a key in music_api.SONG_ADJECTIVES
            e.g. "bouncier", "more acoustic", etc.

    Returns:
        spotify_uri (str): None if cannot make recommendation.
    """
    hits = [
        hit for hit in music_api.get_song_data(song)
        if artist is None or hit["artist_name"].upper() == artist.upper()
    ]
    if len(hits) == 0:
        if artist is None:
            print(f"ERR: Could not find song '{song}'.")
        else:
            print(f"ERR: Could not find song '{song}' by '{artist}'")
        return None
    elif len(hits) > 1:
        print(f"WARN: Found {len(hits)} hits for song '{song}'. Choosing one arbitrarily.")

    cur_song_data = hits[random.randint(0,len(hits)-1)]
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
                print(f"Found '{candidate_song['song_name']}' by {related_artist}")
                return spotify_uri
    print(f"ERR: Could not find a song '{adjective}' than '{song}'.")
    return None

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
