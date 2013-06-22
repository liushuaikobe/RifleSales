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
        resp = self.client.get('/login/')
        self.assertEqual(resp.status_code, 200)
        
        resp = self.client.post('/login/', {'uname' : 'zouliping', 'pwd' : 'zlp'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/checkin/')
        
        salesmanForTest = Salesman.objects.create(user_name = 'test', real_name = 'test_real', pass_word = 'test_pwd')
        
        resp = self.client.post('/login/', {'uname' : 'test', 'pwd' : 'test_pwd'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/checkin/')
        
        
        resp = self.client.post('/login/', {'uname' : 'test', 'pwd' : 'test_pwd_wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], 'please input the correct username and the password.')
        
        resp = self.client.post('/login/', {'uname' : 'test'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], 'please input your user name and the password.')
        
        resp = self.client.post('/login/', {'pwd' : 'test'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], 'please input your user name and the password.')
        
        resp = self.client.post('/login/', {})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], 'please input your user name and the password.')
