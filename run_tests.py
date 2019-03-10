import unittest
"""
Author: John Verwolf.

Import your test below to have it automatically run
by this test-runner.

To run the tests:
    cd intelligent-music-recommender
    python ./run_tests.py
"""
from tests.knowledge_base.test_knowledge_base_api import TestMusicKnowledgeBaseAPI
from tests.knowledge_base.test_db_schema import TestDbSchema
from tests.server.test_webhook import TestWebhook

if __name__ == '__main__':
    unittest.main()
