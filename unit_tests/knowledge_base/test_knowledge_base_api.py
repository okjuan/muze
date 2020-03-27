import unittest

import os

from knowledge_base.api import KnowledgeBaseAPI
from scripts import test_db_utils

class TestMusicKnowledgeBaseAPI(unittest.TestCase):

    def setUp(self):
        DB_path = test_db_utils.create_and_populate_db()
        self.kb_api = KnowledgeBaseAPI(dbName=DB_path)

    def tearDown(self):
        test_db_utils.remove_db()

    def test_get_song_data(self):
        song_data = self.kb_api.get_song_data("Despacito")
        expected_res = dict(
            id=10, song_name="Despacito", artist_name="Justin Bieber",
            duration_ms=222222, popularity=10, valence=0.1,
            spotify_uri='spotify:track:Despacito',
            acousticness=None, danceability=None, energy=None,
            instrumentalness=None, liveness=None, loudness=None,
            speechiness=None, tempo=None, mode=None,
            musical_key=None, time_signature=None,
        )

        self.assertEqual(1, len(song_data), "Expected exactly one result from query for song 'Despacito'.")
        self.assertEqual(song_data[0], expected_res, "Found expected values for song data for 'Despacito'.")

        song_data = self.kb_api.get_song_data(song_id=10)
        self.assertEqual(1, len(song_data), "Expected exactly one result from query for song 'Despacito'.")
        self.assertEqual(song_data[0], expected_res, "Found expected values for song data for 'Despacito'.")

    def test_get_song_data_bad_params(self):
        res = self.kb_api.get_song_data()
        self.assertEqual(res, [], "Expect no results when both song name and ID are ommitted.")

    def test_get_song_data_case_insensitive(self):
        song_data = self.kb_api.get_song_data("dESpAcItO")
        self.assertEqual(1, len(song_data), "Expected exactly one result from query for song 'dESpAcItO'.")
        self.assertEqual(
            song_data[0],
            dict(
                id=10,
                song_name="Despacito",
                artist_name="Justin Bieber",
                duration_ms=222222,
                popularity=10,
                valence=0.1,
                spotify_uri='spotify:track:Despacito',
                acousticness=None, danceability=None, energy=None,
                instrumentalness=None, liveness=None, loudness=None,
                speechiness=None, tempo=None, mode=None,
                musical_key=None, time_signature=None,
            ),
            "Found expected values for song data for 'Despacito'."
        )

        song_data = self.kb_api.get_song_data("bEaUTIful DAY")
        self.assertEqual(1, len(song_data), "Expected exactly one result from query for song 'bEaUTIful DAY'.")
        self.assertEqual(
            song_data[0],
            dict(
                id=12,
                song_name="Beautiful Day",
                artist_name="U2",
                duration_ms=111111,
                popularity=60,
                valence=1.0,
                spotify_uri='spotify:track:BeautifulDay',
                acousticness=None, danceability=None, energy=None,
                instrumentalness=None, liveness=None, loudness=None,
                speechiness=None, tempo=None, mode=None,
                musical_key=None, time_signature=None,
            ),
            "Found expected values for song data for 'Beautiful Day'."
        )

    def test_get_song_data_ambiguous_name(self):
        res = self.kb_api.get_song_data("Sorry")

        self.assertEqual(2, len(res), "Expected exactly two results.")
        self.assertEqual(
            set([14, 15]),
            set([hit["id"] for hit in res]),
            "Found unexpected IDs."
        )

        res = self.kb_api.get_song_data("Sorry", 14)
        self.assertEqual(1, len(res), "Expected exactly one result.")
        self.assertEqual(
            res[0],
            dict(
                id=14, song_name="Sorry", artist_name="Justin Bieber",
                popularity=20, duration_ms=333333,
                valence=0.3, spotify_uri='spotify:track:Sorry',
                acousticness=None, danceability=None, energy=None,
                instrumentalness=None, liveness=None, loudness=None,
                speechiness=None, tempo=None, mode=None,
                musical_key=None, time_signature=None,
            ),
            "Unexpected result contents."
        )

        res = self.kb_api.get_song_data("Sorry", 15)
        self.assertEqual(1, len(res), "Expected exactly one result.")
        self.assertEqual(
            res[0],
            dict(
                id=15, song_name="Sorry", artist_name="The Anti Justin Bieber",
                duration_ms=None, popularity=None, spotify_uri=None,
                acousticness=None, danceability=None, energy=None,
                instrumentalness=None, liveness=None, loudness=None,
                speechiness=None, valence=None, tempo=None, mode=None,
                musical_key=None, time_signature=None,
            ),
            "Unexpected result contents."
        )

    def test_get_song_data_dne(self):
        res = self.kb_api.get_song_data("Not In Database")
        self.assertEqual(res, [], "Expected empty list of results for queried song not in DB.")

    def test_get_artist_data(self):
        artist_data = self.kb_api.get_artist_data("Justin Bieber")
        self.assertEqual(len(artist_data), 1, "Expected exactly one result for artist 'Justin Bieber'.")
        artist_data[0]["genres"] = set(artist_data[0]["genres"])
        self.assertEqual(
            artist_data[0],
            dict(genres=set(["Pop", "Super pop"]), id=1, num_spotify_followers=4000, name="Justin Bieber"),
            "Artist data for 'Justin Bieber' did not match expected.",
        )

    def test_get_artist_data_dne(self):
        artist_data = self.kb_api.get_artist_data("Unknown artist")
        self.assertEqual(artist_data, [], "Expected 'None' result for unknown artist.")

    def test_get_all_song_names(self):
        expected_song_names = set(["Despacito", "Rock Your Body", "Beautiful Day", "In My Blood", "Sorry"])
        res = self.kb_api.get_all_song_names()
        self.assertEqual(set(res), expected_song_names, "Unexpected result from fetching all songs from db.")

    def test_get_all_artist_names(self):
        expected_artist_names = set(["Justin Bieber", "Justin Timberlake", "U2", "Shawn Mendes", "The Anti Justin Bieber"])
        res = self.kb_api.get_all_artist_names()
        self.assertEqual(set(res), expected_artist_names, "Unexpected result from fetching all artists from db.")

    def test_get_songs(self):
        res = self.kb_api.get_songs_by_artist("Justin Bieber")
        self.assertEqual(
            res,
            [dict(song_name="Despacito", id=10), dict(song_name="Sorry", id=14)],
            "Songs retrieved for 'Justin Bieber' did not match expected.",
        )

        res = self.kb_api.get_songs_by_artist("Justin Timberlake")
        self.assertEqual(
            res,
            [dict(song_name="Rock Your Body", id=11)],
            "Songs retrieved for 'Justin Timberlake' did not match expected.",
        )

    def test_get_songs_unknown_artist(self):
        res = self.kb_api.get_songs_by_artist("Unknown artist")
        self.assertEqual(res, [], "Unexpected songs retrieved for unknown artist.")

    def test_songs_are_related_popularity(self):
        self.assertEqual(
            self.kb_api.songs_are_related(12, 10, "less popular"),
            False,
            "'Beautiful Day' is MORE popular than 'Despacito'",
        )

        self.assertEqual(
            self.kb_api.songs_are_related(12, 10, "more popular"),
            True,
            "'Beautiful Day' is MORE popular than 'Despacito'",
        )

    def test_songs_are_related_valence(self):
        self.assertEqual(
            self.kb_api.songs_are_related(12, 10, "more happy"),
            True,
            "'Beautiful Day' is MORE happy than 'Despacito'",
        )

        self.assertEqual(
            self.kb_api.songs_are_related(12, 10, "less happy"),
            False,
            "'Beautiful Day' is MORE happy than 'Despacito'",
        )

    def test_songs_are_related_same_song(self):
        self.assertEqual(
            self.kb_api.songs_are_related(12, 12, "more popular"),
            False,
            "'Beautiful Day' cannot be more popular than itself.",
        )

        self.assertEqual(
            self.kb_api.songs_are_related(12, 12, "more popular"),
            False,
            "'Beautiful Day' cannot be more popular than itself.",
        )

    def test_songs_are_related_unknown_relationship(self):
        self.assertEqual(
            self.kb_api.songs_are_related(12, 10, 'more something'),
            False,
            "Expected return value False when relationship is invalid.",
        )

    def test_songs_are_related_value_missing(self):
        self.assertEqual(
            self.kb_api.songs_are_related(12, 10, 'more dancey'),
            False,
            "Expected return value False when DB does not contain value for given (valid) relationship.",
        )

    def test_find_similar_song(self):
        res = self.kb_api.get_related_entities("Despacito")
        self.assertEqual(
            len(res), 1,
            "Expected only one song similar to \"Despacito\". Found {0}".format(res),
        )
        self.assertEqual(
            res[0], "Rock Your Body",
            "Expected to find \"Rock Your Body\" as similar to \"Despacito\".",
        )

    def test_find_similar_artist(self):
        res = self.kb_api.get_related_entities("Justin Bieber")
        self.assertEqual(
            len(res), 2,
            "Expected exactly two artists similar to Justin Bieber.",
        )
        self.assertEqual(
            res[0], "Justin Timberlake",
            "Expected to find Justin Timberlake as similar to Justin Bieber.",
        )
        self.assertEqual(
            res[1], "Shawn Mendes",
            "Expected to find Justin Timberlake as similar to Justin Bieber.",
        )

    def test_find_similar_to_entity_that_dne(self):
        res = self.kb_api.get_related_entities("Unknown Entity")
        self.assertEqual(res, [])

    def test_get_related_genres(self):
        genre_rel_str = self.kb_api.approved_relations["genre"]
        rel_genres = self.kb_api.get_related_entities("Justin Bieber", rel_str=genre_rel_str)
        self.assertEqual(set(rel_genres), set(["Pop", "Super pop"]),
            "Did not find expected related genres for artist 'Justin Bieber'")

        rel_genres = self.kb_api.get_related_entities("Justin Timberlake", rel_str=genre_rel_str)
        self.assertEqual(rel_genres, ["Pop"],
            "Did not find expected related genres for artist 'Justin Timberlake'")

    def test_connect_entities_by_similarity(self):
        res = self.kb_api.get_related_entities("Shawn Mendes")
        self.assertEqual(len(res), 0)

        res = self.kb_api.connect_entities("Shawn Mendes", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, True, "")

        res = self.kb_api.get_related_entities("Shawn Mendes")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "Justin Timberlake")

    def test_connect_entities_by_genre(self):
        genre_rel_str = self.kb_api.approved_relations["genre"]
        res = self.kb_api.get_related_entities("Shawn Mendes", rel_str=genre_rel_str)
        self.assertEqual(len(res), 0)

        res = self.kb_api.connect_entities("Shawn Mendes", "Pop", "of genre", 100)
        self.assertEqual(res, True, "")

        res = self.kb_api.get_related_entities("Shawn Mendes", rel_str=genre_rel_str)
        self.assertEqual(len(res), 1, "Expected to find exactly one related genre for 'Shawn Mendes'.")
        self.assertEqual(res[0], "Pop", "Found unexpected genre for 'Shawn Mendes'.")

    def test_rejects_connect_ambiguous_entities(self):
        self.kb_api.add_artist("Artist and Song name clash")
        self.kb_api.add_song("Artist and Song name clash", "U2")

        res = self.kb_api.connect_entities("Artist and Song name clash", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, False, "")

    def test_get_node_ids_by_entity_type(self):
        node_ids_dict = self.kb_api.get_node_ids_by_entity_type("Justin Bieber")
        all_entity_types = list(node_ids_dict.keys())
        self.assertEqual(
            all_entity_types,
            ["artist"],
            "Expected to find (only) entities of type 'artist' for 'Justin Bieber', but got: {}"
                .format(node_ids_dict)
        )
        self.assertEqual(
            len(node_ids_dict.get("artist")),
            1,
            "Expected to find exactly one entity of type 'artist' for 'Justin Bieber', but got: {}"
                .format(node_ids_dict)
        )

        self.kb_api.add_artist("Song and Artist name")
        self.kb_api.add_song("Song and Artist name", "U2")

        node_ids_dict = self.kb_api.get_node_ids_by_entity_type("Song and Artist name")
        alphabetized_entity_types = sorted(list(node_ids_dict.keys()))
        self.assertEqual(
            alphabetized_entity_types,
            ["artist", "song"],
            "Expected to find (exactly) two entity types: 'artist' and 'song', but got: {}"
                .format(node_ids_dict)
        )

    def test_get_matching_node_ids(self):
        node_ids = self.kb_api._get_matching_node_ids("Justin Bieber")
        self.assertEqual(len(node_ids), 1,
            "Expected to find exactly one matching node for 'Justin Bieber', but got: {}"
                .format(node_ids)
        )

    def test_get_matching_node_ids_empty(self):
        node_ids = self.kb_api._get_matching_node_ids("Unknown artist")
        self.assertEqual(len(node_ids), 0,
            "Expected to find no matching node for 'Unknown artist', but got: {}"
                .format(node_ids)
        )

    def test_add_artist(self):
        sample_genres = ["Pop", "Very pop", "Omg so pop"]
        new_artist_node_id = self.kb_api.add_artist("Heart", genres=sample_genres, num_spotify_followers=1)
        self.assertNotEqual(new_artist_node_id, None, "Failed to add artist 'Heart' to knowledge base.")

        artist_data = self.kb_api.get_artist_data("Heart")
        self.assertEqual(len(artist_data), 1, "Expected unique match for artist 'Heart'.")

        artist_data = artist_data[0]
        artist_data["genres"] = set(artist_data["genres"])

        self.assertEqual(
            artist_data,
            dict(
                name="Heart",
                id=new_artist_node_id,
                genres=set(sample_genres),
                num_spotify_followers=1,
            ),
            "Did not find expected genres for artist 'Heart'.",
        )

    def test_reject_add_artist_already_exists(self):
        artist_node_id = self.kb_api.get_artist_data("Justin Bieber")[0]["id"]
        res = self.kb_api.add_artist("Justin Bieber")
        self.assertEqual(res, artist_node_id, "Expected rejection of attempt to add artist 'Justin Bieber' to knowledge base.")

    def test_add_artist_omitted_opt_params(self):
        res = self.kb_api.add_artist("Heart")
        self.assertNotEqual(res, None, "Failed to add artist 'Heart' to knowledge base.")

        artist_data = self.kb_api.get_artist_data("Heart")
        self.assertEqual(len(artist_data), 1, "Expected unique match for artist 'Heart'.")
        self.assertEqual(artist_data[0]["name"], "Heart", "Expected match for artist 'Heart'.")
        self.assertEqual(artist_data[0]["genres"], [], "Expected no genres for artist 'Heart'.")
        self.assertEqual(artist_data[0]["num_spotify_followers"], None, "Expected no genres for artist 'Heart'.")

    def test_add_song(self):
        new_song_node_id = self.kb_api.add_song(
            "Heart",
            "Justin Bieber",
            duration_ms=11111,
            popularity=100,
            spotify_uri="spotify:track:Heart",
            audio_features=dict(energy=0.5),
        )
        self.assertNotEqual(new_song_node_id, None, "Failed to add song 'Heart' by artist 'Justin Bieber' to knowledge base.")

        song_data = self.kb_api.get_song_data("Heart")
        self.assertEqual(len(song_data), 1, "Expected exactly one result.")

        song_data = song_data[0]
        self.assertEqual(
            song_data,
            dict(
                id=new_song_node_id,
                song_name="Heart",
                artist_name="Justin Bieber",
                duration_ms=11111,
                popularity=100,
                spotify_uri="spotify:track:Heart",
                energy=0.5,
                acousticness=None, danceability=None,
                instrumentalness=None, liveness=None, loudness=None,
                speechiness=None, valence=None, tempo=None, mode=None,
                musical_key=None, time_signature=None,
            ),
            "Received unexpected song data",
        )

    def test_add_song_omitted_opt_params(self):
        new_song_node_id = self.kb_api.add_song("What do you mean?", "Justin Bieber")
        self.assertNotEqual(new_song_node_id, None, "Failed to add song 'sorry' by artist 'Justin Bieber' to knowledge base.")

        song_data = self.kb_api.get_song_data("What do you mean?")
        self.assertEqual(len(song_data), 1, "Expected exactly one result.")

        song_data = song_data[0]
        self.assertEqual(
            song_data,
            dict(
                id=new_song_node_id,
                song_name="What do you mean?",
                artist_name="Justin Bieber",
                duration_ms=None, popularity=None, spotify_uri=None,
                acousticness=None, danceability=None, energy=None,
                instrumentalness=None, liveness=None, loudness=None,
                speechiness=None, valence=None, tempo=None, mode=None,
                musical_key=None, time_signature=None,
            ),
            "Received unexpected song data"
        )

    def test_add_song_with_all_audio_features(self):
        valid_audio_features = dict(
            acousticness=1, danceability=1, energy=1, instrumentalness=1,
            liveness=1, loudness=0, speechiness=1, valence=1, tempo=1,
            mode="major", musical_key=1, time_signature=3,
        )
        new_song_id = self.kb_api.add_song(
            "Song with all audio features",
            "Justin Bieber",
            audio_features=valid_audio_features,
        )

        song_data = self.kb_api.get_song_data("Song with all audio features")
        self.assertEqual(
            dict(
                id=new_song_id,
                song_name="Song with all audio features",
                artist_name="Justin Bieber",
                duration_ms=None, popularity=None, spotify_uri=None,
                acousticness=1.0, danceability=1.0, energy=1.0, instrumentalness=1.0,
                liveness=1.0, loudness=0.0, speechiness=1.0, valence=1.0, tempo=1.0,
                mode="major", musical_key=1, time_signature=3,
            ),
            song_data[0],
            "Retrieved song data did not match expected.",
        )

    def test_add_duplicate_song_for_different_artist(self):
        new_song_node_id = self.kb_api.add_song("Despacito", "Justin Timberlake")
        self.assertNotEqual(new_song_node_id, None, "Failed to add song 'Despacito' by artist 'Justin Timberlake' to knowledge base.")

        res = self.kb_api.get_song_data("Despacito")
        self.assertEqual(len(res), 2, "Expected exactly one match for song 'Despacito'.")

        artists = set([res[0]["artist_name"], res[1]["artist_name"]])
        self.assertEqual(artists, set(["Justin Bieber", "Justin Timberlake"]),
            "Expected to find duplicate artists 'Justin Bieber' and 'Justin Timberlake' for song 'Despacito')")

    def test_reject_add_song_already_exists(self):
        res = self.kb_api.add_song("Despacito", "Justin Bieber")
        self.assertEqual(res, None, "Expected rejection of attempt to add song 'Despacito' by 'Justin Bieber' to knowledge base.")

    # The logic tested here is currently implemented in the KR API
    # However, if it is moved to the schema (e.g. trigger functions),
    # then this test can be moved to the schema test module
    def test_new_song_with_unknown_artist_rejected(self):
        res = self.kb_api.add_song("Song by Unknown Artist", "Unknown artist")
        self.assertEqual(res, None, "Expected song with unknown artist to be rejected")

        res = self.kb_api.get_song_data("Song by Unknown Artist")
        self.assertEqual(len(res), 0,
            "Insertion of song with unknown artist should not have been added to nodes table")

    def test_add_genre(self):
        node_id = self.kb_api.add_genre("hip hop")
        self.assertEqual(type(node_id), int,
            "Genre addition appears to have failed: expected int return value (node id) on valid attempt to add genre.")

        res = self.kb_api.add_genre("hip hop")
        self.assertEqual(res, node_id, "Expected original node id to be fetched when attempting to add duplicate genre.")

    def test_add_genre_creates_node(self):
        res = self.kb_api.add_genre("hip hop")
        self.assertEqual(type(res), int,
            "Genre addition appears to have failed: expected int return value (node id) on valid attempt to add genre.")

        entities = self.kb_api.get_node_ids_by_entity_type("hip hop")
        self.assertIn("genre", entities, "Expected to find node associated with genre 'hip hop'.")

    def test_get_node_ids_by_entity_type(self):
        res = self.kb_api.get_node_ids_by_entity_type("Justin Timberlake")
        self.assertTrue("artist" in res,
            "Expected to find an 'artist' entity with name 'Justin Timberlake', but got: {0}".format(res))
        self.assertEqual(len(res["artist"]), 1,
            "Expected to find exactly one entity (of type 'artist') with name 'Justin Timberlake', but got: {0}".format(res))

        res = self.kb_api.get_node_ids_by_entity_type("Despacito")
        self.assertTrue("song" in res,
            "Expected to find an 'song' entity with name 'Despacito', but got: {0}".format(res))
        self.assertEqual(len(res["song"]), 1,
            "Expected to find exactly one entity (of type 'song') with name 'Despacito', but got: {0}".format(res))

        res = self.kb_api.get_node_ids_by_entity_type("Unknown entity")
        self.assertEqual(res, {}, "Expected no results from query for unknown entity, but got {}".format(res))


if __name__ == '__main__':
    unittest.main()
