import unittest
import app.server as endpoint

# TODO: use test DB
class TestServer(unittest.TestCase):
    def setUp(self):
        self.test_app = endpoint.app

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
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "happier")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "sadder")

        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

        with self.test_app.app_context():
            spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "dancier")

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
