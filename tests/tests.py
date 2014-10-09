import unittest
import requests
from kiigameEditor import client


class Tests(unittest.TestCase):

    def test_tests_should_work(self):
        self.assertEqual(True, True)

    def test_editor_should_get_Hello_World_from_server(self):
        self.assertEqual(requests.get(
            'http://localhost:5000/hello_world').text, 'Hello World!')

    def test_can_open_test_file(self):
        c = client.Client()
        f = c.get_test_file()
        self.assertIsNotNone(f)

    def test_can_upload_test_file(self):
        c = client.Client()
        self.assertEqual(c.test_upload(
            '').status_code, 200)

    def test_can_download_test_file(self):
        self.assertEqual(client.Client()
            .download_test_file('test.txt').status_code, 200)

    def test_get_game_files(self):
        s = client.Client().get_game_files('../gamedata/latkazombit')
        self.assertEqual(True, s)
