import unittest
import app.server as endpoint

# TODO: use test DB
class TestServer(unittest.TestCase):
    def setUp(self):
        self.test_app = endpoint.app

    def test_find_song(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.find_song("thank u, next", artist=None)

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_find_song_with_artist(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.find_song("thank u, next", artist="Ariana Grande")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_find_song_with_wrong_artist(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.find_song("thank u, next", artist="Alessia Cara")

        self.assertEqual(msg[:13], "Unfortunately", "Expected no song to be found.")
        self.assertEqual(spotify_uri, None, "Expected no Spotify URI")

    def test_find_song_unknown(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.find_song("some unknown song", artist=None)

        self.assertEqual(msg[:13], "Unfortunately", "Expected no song to be found.")
        self.assertEqual(spotify_uri, None, "Expected no Spotify URI")

    def test_get_finegrained_recommendation_song_unknown(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation(
                "some unknown song",
                "more acoustic",
            )

        self.assertEqual(msg[:13], "Unfortunately", "Expected no song to be found.")
        self.assertEqual(spotify_uri, None, "Expected no Spotify URI")

    def test_get_finegrained_recommendation_bad_adjective(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("thank u, next", "more musical")

        self.assertEqual(msg[:13], "Unfortunately", "Expected no song to be found.")
        self.assertEqual(spotify_uri, None, "Expected no Spotify URI")

    def test_get_finegrained_recommendation_more_acoustic(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("thank u, next", "more acoustic")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_less_acoustic(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "less acoustic")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_happier(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "happier")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_sadder(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "sadder")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_dancier(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "dancier")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_less_dancey(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("7 rings", "less dancey")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_less_acoustic_related_artist(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("bad idea", "less acoustic")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")

    def test_get_finegrained_recommendation_more_popular(self):
        with self.test_app.app_context():
            msg, spotify_uri = endpoint.get_finegrained_recommendation("bad idea", "more popular")

        self.assertEqual(msg[:5], "Found", "Expected to find a song.")
        self.assertEqual(spotify_uri[:14], "spotify:track:", "Expected to receive Spotify URI")
