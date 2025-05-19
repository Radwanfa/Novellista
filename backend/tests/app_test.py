import unittest
import sys
sys.path.insert(0, "/home/radwanfa/Documents/Novellista/backend")
from app import app

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.form_data = {
            'username': 'someone',
            'password': '123',
            'Rpassword': '122'
        }

    def test_register(self):
        response = self.app.post("/api/register", data=self.form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "fail", "message": "wachtwoorden kloppen niet. Heb je een spelfout gemaakt?"})

if __name__ == '__main__':
    unittest.main()