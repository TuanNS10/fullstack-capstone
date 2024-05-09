import json
from dotenv import load_dotenv
import os
import requests
import unittest
from flask_sqlalchemy import SQLAlchemy
from config import bearer_tokens

from app import create_app

load_dotenv()
database_path = os.getenv("DATABASE_URL")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_path = database_path
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client
        self.base_url = 'http://localhost:5000'

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
        
        self.casting_assistant_auth_header = {
        'Authorization': bearer_tokens['casting_assistant']
        }

        self.casting_director_auth_header = {
            'Authorization': bearer_tokens['casting_director']
        }

        self.executive_producer_auth_header = {
            'Authorization': bearer_tokens['executive_producer']
        }

        self.movie = {
            "title": "With you",
            "release_date": "2024-10-05"
        }

        self.actor = {
            "name": "Sanh Tuan",
            "gender": 'M',
            "age": 25,           
            "movie_id": 2
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_actors(self):
        res = requests.get(f'{self.base_url}/actors', headers=self.casting_assistant_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))
    
    def test_get_movies(self):
        res = requests.get(f'{self.base_url}/movies', headers=self.casting_assistant_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["movies"]), type([]))
    
    def test_get_actors_by_producer(self):

        res = requests.get(f'{self.base_url}/actors', headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))
    
    def test_get_actor_fail(self):
        res = requests.get(f'{self.base_url}/actors')
        data = res.json()

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(type(data["message"]), type(""))
    
    def test_create_movies(self):
        res = requests.post(f'{self.base_url}/movies', json=self.movie, headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
    
    def test_create_actors(self):
        res = requests.post(f'{self.base_url}/actors', json=self.actor, headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
    
    def test_create_movies_fail_400(self):
        movie_fail = {"title": "Movie faile 400"}
        res = requests.post(f'{self.base_url}/movies',json=movie_fail, headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Missing field for Movie")

    def test_create_movies_fail_403(self):
        movie_fail = {"title": "Movie fail 403"}
        res = requests.post(f'{self.base_url}/movies',json=movie_fail, headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
    
    def test_create_actors_fail_400(self):
        actor_fail = {"title": "Actors faile 400"}
        res = requests.post(f'{self.base_url}/actors',json=actor_fail, headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Missing field for Movie")

    def test_create_actors_fail_403(self):
        actor_fail = {"title": "Actors fail 403"}
        res = requests.post(f'{self.base_url}/actors',json=actor_fail, headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
    
    def test_update_movie(self):
        movie_id = 2
        new_title = "With you 2"
        res = requests.patch(f'{self.base_url}/movies/{movie_id}',
            json={'title': new_title},
            headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated']['id'], movie_id)
        self.assertEqual(data['updated']['title'], new_title)

    def test_update_movie(self):
        movie_id = 3
        new_title = "With you 3"
        res = requests.patch(f'{self.base_url}/movies/{movie_id}',
            json={'title': new_title},
            headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated']['id'], movie_id)
        self.assertEqual(data['updated']['title'], new_title)

    def test_update_movie_fail_404(self):
        movie_id = -1
        res = requests.patch(f'{self.base_url}/movies/{movie_id}',
            headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_update_actor(self):
        actor_id = 3
        new_name = "Thuc Doan"
        new_age = 24
        res = requests.patch(f'{self.base_url}/actors/{actor_id}',
            json={'name': new_name, 'age': new_age},
            headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated']['id'], actor_id)
        self.assertEqual(data['updated']['name'], new_name)
        self.assertEqual(data['updated']['age'], new_age)

    def test_update_actor_fail_404(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        actor_id = -1
        res = requests.patch(f'{self.base_url}/actors/{actor_id}',
            headers=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_update_actor_fail_403(self):
        actor_id = 6
        res = requests.patch(f'{self.base_url}/actors/{actor_id}',
            headers=self.casting_assistant_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_delete_movie(self):
        movie_id = 1
        res = requests.delete(f'{self.base_url}/movies/{movie_id}', json=self.executive_producer_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], movie_id)

    def test_delete_movie_fail_404(self):
        movie_id = -1
        res = requests.delete(f'/movies/{movie_id}', headers=self.executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_movie_fail_403(self):
        movie_id = 3
        res = self.client().delete(f'/movies/{movie_id}', headers=self.casting_assistant_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_delete_actor(self):
        actor_id = 1
        res = requests.delete(f'/actors/{actor_id}',
            headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], actor_id)

    def test_delete_actor_fail_404(self):
        actor_id = -1
        res = requests.delete(f'/actors/{actor_id}', headers=self.casting_director_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_actor_fail_403(self):
        actor_id = 10
        res = requests.delete(f'/actors/{actor_id}', headers=self.casting_assistant_auth_header)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

if __name__ == "__main__":
    unittest.main()
