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
        self.assertNotEqual(
            msg,
            "Unfortunately, I couldn't find any songs similar to but more obscure than thank u, next.",
            "Woops!",
        )

    def test_get_more_obscure_song_none_found(self):
        with self.test_app.app_context():
            res = endpoint.get_more_obscure_song("If Only")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Unfortunately, I couldn't find any songs similar to but more obscure than If Only.",
            "Woops!",
        )
