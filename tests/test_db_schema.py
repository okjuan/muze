from contextlib import closing
from knowledge_base.api import KnowledgeBaseAPI
from scripts import test_db_utils

import os
import unittest

class TestDbSchema(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        DB_path = test_db_utils.create_and_populate_db()
        self.kb_api = KnowledgeBaseAPI(dbName=DB_path)

    @classmethod
    def tearDownClass(self):
        test_db_utils.remove_db()

    def test_rejects_unknown_entity(self):
        res = self.kb_api.connect_entities("Unknown Entity", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, False,
            "Expected attempt to connect an unknown entity to fail.")

        res = self.kb_api.get_related_entities("Unknown Entity")
        self.assertEqual(res, [])

    def test_rejects_score_out_of_range(self):
        res = self.kb_api.connect_entities("Justin Timberlake", "Justin Timberlake", "similar to", -1)
        self.assertEqual(res, False,
            "Expected attempt to connect entities with score out-of-range to fail.")

        res = self.kb_api.get_related_entities("Justin Timberlake")
        self.assertEqual(len(res), 0)

    def test_rejects_duplicate_edge(self):
        res = self.kb_api.connect_entities("Justin Bieber", "Justin Timberlake", "similar to", 1)
        self.assertEqual(res, False,
            "Expected attempt to add a duplicate edge to fail.")

    def test_edges_not_null_constraints(self):
        res = self.kb_api.connect_entities(None, "Justin Timberlake", "similar to", 1)
        self.assertEqual(res, False,
            "Expected 'None' value for artist to be rejected.")

        res = self.kb_api.connect_entities("U2", "U2", None, 1)
        self.assertEqual(res, False,
            "Expected 'None' value for edge type to be rejected.")

        res = self.kb_api.connect_entities("U2", "U2", "similar to", None)
        self.assertEqual(res, False,
            "Expected 'None' value for edge score to be rejected.")

    def test_entities_not_null_constraints(self):
        res = self.kb_api.add_artist(None)
        self.assertEqual(res, None,
            "Expected 'None' value for artist to be rejected.")

        res = self.kb_api.add_song("Song name", None)
        self.assertEqual(res, None,
            "Expected 'None' value for artist to be rejected.")

        res = self.kb_api.add_song(None, "Artist name")
        self.assertEqual(res, None,
            "Expected 'None' value for artist to be rejected.")

        node_id = self.kb_api._add_node(None, "artist")
        self.assertEqual(node_id, None,
            "Expected 'None' value for entity name to be rejected.")

        node_id = self.kb_api._add_node("Some entity", None)
        self.assertEqual(node_id, None,
            "Expected 'None' value for entity type to be rejected.")

if __name__ == '__main__':
    unittest.main()
