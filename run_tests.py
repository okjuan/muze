import unittest
"""
Author: John Verwolf.

Import your test below to have it automatically run
by this test-runner.

To run the tests:
    cd intelligent-music-recommender
    python ./run_tests.py
"""
from unit_tests.knowledge_base.test_knowledge_base_api import TestMusicKnowledgeBaseAPI
from unit_tests.knowledge_base.test_db_schema import TestDbSchema
from unit_tests.app.server.test_server import TestServer

if __name__ == '__main__':
    unittest.main()
