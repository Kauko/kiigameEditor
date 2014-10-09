import unittest
import requests

class Tests(unittest.TestCase):

    def test_tests_should_work(self):
        self.assertEqual(True, True)

    def test_editor_should_get_Hello_World_from_server(self):
        self.assertEqual(requests.get('http://localhost:5000'), 'Hello World!')
