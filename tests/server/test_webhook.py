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

    def test_get_finegrained_recommendation_bad_adjective(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("thank u, next", "more musical")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Unfortunately, I could not find a song 'more musical' than 'thank u, next'.",
            "Expected to reject given adjective.",
        )

    def test_get_finegrained_recommendation_more_acoustic(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("thank u, next", "more acoustic")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found '7 rings' by Ariana Grande",
            "Expected to reject given adjective.",
        )

    def test_get_finegrained_recommendation_less_acoustic(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("7 rings", "less acoustic")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'break up with your girlfriend, i'm bored' by Ariana Grande",
            "Did not find expected song.",
        )

    def test_get_finegrained_recommendation_happier(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("7 rings", "happier")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'break up with your girlfriend, i'm bored' by Ariana Grande",
            "Did not find expected song.",
        )

    def test_get_finegrained_recommendation_sadder(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("7 rings", "sadder")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'needy' by Ariana Grande",
            "Did not find expected song.",
        )

    def test_get_finegrained_recommendation_dancier(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("7 rings", "dancier")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'bad idea' by Ariana Grande",
            "Did not find expected song.",
        )

    def test_get_finegrained_recommendation_less_dancey(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation("7 rings", "less dancey")
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'break up with your girlfriend, i'm bored' by Ariana Grande",
            "Did not find expected song.",
        )

    def test_get_finegrained_recommendation_less_acoustic_related_artist(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation(
                "bad idea",
                "less acoustic",
            )
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'Trust My Lonely' by Alessia Cara",
            "Expected to reject given adjective.",
        )

    def test_get_finegrained_recommendation_more_popular(self):
        with self.test_app.app_context():
            res = endpoint.get_finegrained_recommendation(
                "bad idea",
                "more popular",
            )
        msg = res._messages[0]['text']['text'][0]
        self.assertEqual(
            msg,
            "Found 'break up with your girlfriend, i'm bored' by Ariana Grande",
            "Did not find expected song.",
        )
