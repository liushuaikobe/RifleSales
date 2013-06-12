"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from login.models import Salesman


class LoginTestCase(TestCase):
    fixtures = ['login_views_test_data.json']
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        
        salesmanForTest = Salesman.objects.create(user_name = 'test', real_name = 'test_real', pass_word = 'test_pwd')
        resp = self.client.post('/login/', {'uname' : 'test', 'pwd' : 'test_pwd'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/checkin/')
        
        resp = self.client.post('/login/', {'uname' : 'test', 'pwd' : 'test_pwd_wrong'})
        self.assertEqual(resp.status_code, 200)
