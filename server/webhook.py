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


if __name__ == '__main__':
    app.run(debug=True)
