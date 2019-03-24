import unittest
import server.webhook as endpoint

# TODO: use test DB
class TestWebhook(unittest.TestCase):
    def setUp(self):
        self.test_app = endpoint.app

    def test_get_more_obscure_song(self):
        with self.test_app.app_context():
            res = endpoint.get_more_obscure_song("thank u, next")
        msg = res._messages[0]['text']['text'][0]
        self.assertIn("Found", msg, "Expected to find a song.")

    def test_get_more_obscure_song_none_found(self):
        with self.test_app.app_context():
            res = endpoint.get_more_obscure_song("If Only")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Unfortunately, I couldn't find any songs similar to but more obscure than If Only.",
            "Expected not to find a song.",
        )

    def test_find_song(self):
        with self.test_app.app_context():
            res = endpoint.find_song("thank u, next", artist=None)
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found thank u, next by Ariana Grande",
            "Expected to find a song.",
        )

    def test_find_song_with_artist(self):
        with self.test_app.app_context():
            res = endpoint.find_song("thank u, next", artist="Ariana Grande")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found thank u, next by Ariana Grande",
            "Expected to find a song.",
        )

    def test_find_song_with_wrong_artist(self):
        with self.test_app.app_context():
            res = endpoint.find_song("thank u, next", artist="Alessia Cara")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Unfortunately, I couldn't find thank u, next by Alessia Cara.",
            "Expected to find a song.",
        )

    def test_find_song_unknown(self):
        with self.test_app.app_context():
            res = endpoint.find_song("some unknown song", artist=None)
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Unfortunately, I couldn't find some unknown song.",
            "Expected to find a song.",
        )
