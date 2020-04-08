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
MAX_RECOMMENDATIONS_PER_SONG = 15 #arbitrary

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
    song, adjective, spotify_uri = data.get("song"), data.get("adjective"), data.get("spotify_uri")
    song_data = _get_song_data(song, spotify_uri)
    if song_data is None:
        print("ERR: Could not get recommendation based on given song because its data could not be found based on given info: ", data)
        socket_io.emit("msg", data=f"Could not find song '{song}'")
        return

    on_find = lambda spotify_uri: socket_io.emit("new song", data=dict(spotify_uris=[spotify_uri]))
    if adjective is None:
        print(f"Received request for song similar to '{song}'")
        num_hits = get_similar_songs(song_data, on_find)
    else:
        print(f"Received '{adjective}' request for song '{song}'")
        num_hits = get_finegrained_recommendations(song_data, adjective, on_find)

    print(f"Found {num_hits} recommendations for song '{song}'")
    if num_hits == 0:
        socket_io.emit("msg", data=f"Could not find recommendations for song '{song}'")

def _get_song_data(song_name, spotify_uri):
    for matching_song in music_api.get_song_data(song_name):
        if matching_song['spotify_uri'] == spotify_uri:
            return matching_song
    print(f"ERR: Could not find song '{song_name}'.")
    return None

def get_similar_songs(song_data, on_find, max_songs=MAX_RECOMMENDATIONS_PER_SONG):
    """Encapsulates interaction with music API for getting a recommendation.

    Params:
        song_data (dict): as returned by music api.
        on_find (func): what to do with a song's spotify uri each time a recommendation is found.
            e.g. add to a list, or emit an event to the client
        max_songs (int).

    Returns:
        num_hits (int).
    """
    recommended_songs = music_api.get_related_entities(song_data['song_name'])
    if recommended_songs == []:
        cur_artist = song_data['artist_name']
        related_artists = music_api.get_related_entities(cur_artist) + [cur_artist]
        if len(related_artists) > 0:
            # TODO: use music api IDs (as soon as other get_related_entities called above also returns them)
            recommended_songs = [x['song_name']
                for x in music_api.get_songs_by_artist(
                    related_artists[random.randint(0, len(related_artists)-1)]
                )
            ]
    # pick random subset
    for song in random.sample(recommended_songs, min(len(recommended_songs), max_songs)):
        spotify_uri = _get_spotify_uri(song)
        if spotify_uri is not None:
            on_find(spotify_uri)
    return len(recommended_songs)

def _get_spotify_uri(song_name):
    hits = music_api.get_song_data(song_name=song_name)
    if hits == []:
        print(f"ERR: Couldn't find song info for: '{song_name}'")
        return None
    elif len(hits) > 1:
        print(f"WARN: Found {len(hits)} hits for song '{song_name}'. Choosing one arbitrarily.")
    return hits[0]['spotify_uri']

def get_finegrained_recommendations(song_data, adjective, on_find, max_songs=MAX_RECOMMENDATIONS_PER_SONG, artist=None):
    """
    Params:
        song_data (dict): as returned by music api.
        adjective (str): should be a key in music_api.SONG_ADJECTIVES
            e.g. "bouncier", "more acoustic", etc.
        on_find (func): what to do with a song's spotify uri each time a recommendation is found.
            e.g. add to a list, or emit an event to the client
        max_songs (int).

    Returns:
        num_hits (int).
    """
    cur_artist = song_data["artist_name"]
    cur_song_id = song_data["id"]

    rel_artists = music_api.get_related_entities(cur_artist) + [cur_artist]
    random.shuffle(rel_artists)
    num_hits = 0
    for related_artist in rel_artists:
        songs_by_rel_artist = music_api.get_songs_by_artist(related_artist)
        random.shuffle(songs_by_rel_artist)
        for candidate_song in songs_by_rel_artist:
            if music_api.songs_are_related(candidate_song["id"], cur_song_id, rel_str=adjective):
                song_data = music_api.get_song_data(candidate_song["song_name"], candidate_song["id"])
                on_find(song_data[0]["spotify_uri"])
                num_hits += 1

                print(f"Found '{candidate_song['song_name']}' by {related_artist}.")

                if num_hits >= max_songs:
                    return num_hits
    return num_hits

@socket_io.on("get random song")
def get_random_song():
    socket_io.emit(
        "new song",
        data=dict(spotify_uris=[music_api.get_random_song()]),
    )


if __name__ == '__main__':
    # on Heroku, the port is an environment variable
    port = int(os.environ.get("PORT", 5000))
    print("Running muze service on port:", port)
    socket_io.run(app, host="0.0.0.0", port=port)
