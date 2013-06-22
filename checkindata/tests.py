"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from login.models import Salesman
from viewdata.models import Commission

from checkindata.views import getCurrentDate, calcCommission
from viewdata.views import getCurrentMonthCommission


class SimpleTest(TestCase):
    def test_calc_commission(self):
        salesmanForTest = Salesman.objects.create(user_name = 'test', real_name = 'test_real', pass_word = 'test_pwd')
        
        resp = self.client.post('/login/', {'uname' : 'test', 'pwd' : 'test_pwd'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/checkin/')
        
        resp = self.client.post('/checkin/', {'location' : 'location1', 'merchandise' : 'lock', 'quantity' : 10})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/checkin/', {'location' : 'location2', 'merchandise' : 'stock', 'quantity' : 10})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/checkin/', {'location' : 'location2', 'merchandise' : 'barrel', 'quantity' : 10})
        self.assertEqual(resp.status_code, 200)
        
        calcCommission(salesmanForTest, getCurrentDate(), False)
        
        self.assertEqual(getCurrentMonthCommission(salesmanForTest, getCurrentDate()), (10 * 45 + 10 * 30 + 10 * 25) * 0.1)
        
        
        