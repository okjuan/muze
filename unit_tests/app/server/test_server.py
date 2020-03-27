import unittest
import app.server as endpoint
from knowledge_base.api import KnowledgeBaseAPI
from scripts import test_db_utils

# TODO: use test DB
class TestServer(unittest.TestCase):
    def setUp(self):
        self.test_app = endpoint.app

    def test_get_similar_song_returns_spotify_uri(self):
        with self.test_app.app_context():
            spotify_uri = endpoint.get_similar_song("thank u, next")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_similar_song_bad_song_name_returns_None(self):
        with self.test_app.app_context():
            spotify_uri = endpoint.get_similar_song("asdfasdf")

        self.assertEqual(spotify_uri, None, "Expected to receive None.")

    def test_get_finegrained_recommendation_song_unknown(self):
        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation(
                "some unknown song",
                "more acoustic",
            )

        self.assertEqual(spotify_uri, None, "Expected no Spotify URI")

    def test_get_finegrained_recommendation_bad_adjective(self):
        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("thank u, next", "more musical")

        self.assertEqual(spotify_uri, None, "Expected no Spotify URI")

    def test_get_finegrained_recommendation(self):
        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("thank u, next", "more acoustic")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "less acoustic")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "more happy")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "less happy")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "more dancey")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "less dancey")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("bad idea", "less acoustic")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("bad idea", "more popular")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")
