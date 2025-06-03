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
            'Rpassword': '122',
            'session': '',
            'userId': '',
            'story': '“You plottin’ on me, girl? Tryin’ to get me out of here so that you can rig up a trap on my desk?” He stuck out a hammy finger, stained purple.'
        }
        

    def register(self):
        self.form_data['Rpassword'] = '123'
        response = self.app.post("/api/register", data=self.form_data)
        return response.json
    
    def save_story(self):
        id = self.register()
        self.form_data['userId'] = id['id']
        response = self.app.post("/api/save_story", data=self.form_data)
        return response.json

    def test_get_session(self):
        session = self.register()
        self.form_data['session'] = session['string']
        response = self.app.post("/api/get_session", data=self.form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'someone')
    
    def test_login(self):
        self.register()
        self.form_data['password'] = '123'
        self.form_data['username'] = 'someone'
        response = self.app.post("/api/login", data=self.form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        
        self.form_data['session'] = response.json['string']

    def test_login_not_found(self):
        self.form_data['username'] = 'someon'
        response = self.app.post("/api/login", data=self.form_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json['status'], 'fail')

    def test_login_mismatch(self):
        self.register()
        self.form_data['password'] = '122'
        response = self.app.post("/api/login", data=self.form_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'fail')

    def test_register(self):
        self.form_data['Rpassword'] = '123'
        response = self.app.post("/api/register", data=self.form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    def test_register_mismatch(self):
        response = self.app.post("/api/register", data=self.form_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {"status": "fail", "message": "wachtwoorden kloppen niet. Heb je een spelfout gemaakt?"})

    def test_get_stories(self):
        self.save_story()
        id = self.register()
        response = self.app.post("/api/get_stories", headers={
            'userId': id['id'],
        })
        self.assertEqual(response.status_code, 200)
    
    def test_save_story(self):
        id = self.register()
        self.form_data['userId'] = id['id']
        response = self.app.post("/api/save_story", data=self.form_data)
        self.assertEqual(response.status_code, 200)

    def test_get_story(self):
        id = self.save_story()
        response = self.app.get(f"/api/get_story?id={id['id']}")
        self.assertEqual(response.status_code, 200)
    

if __name__ == '__main__':
    unittest.main()