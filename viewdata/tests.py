"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from login.models import Salesman
from viewdata.models import Commission

from checkindata.views import getCurrentDate, calcCommission


class SimpleTest(TestCase):
    fixtures = ['login_views_test_data.json', \
                'checkindata_views_test_data.json', \
                'viewdata_views_test_data.json']
    def test_salesman_viewCurrent(self):
        # get the viewcurrent page directly without having login
        resp = self.client.get('/viewcurrent/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/')
        
        # a real salesman
        crtSalesman = Salesman.objects.get(user_name = 'zouliping')
        date = getCurrentDate()
        
        resp = self.client.post('/login/', {'uname' : crtSalesman.user_name, 'pwd' : crtSalesman.pass_word})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/checkin/')
        
        resp = self.client.get('/viewcurrent/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('commissionVal' in resp.context)
        self.assertEqual(resp.context['commissionVal'], Commission.objects.get(whose = crtSalesman.id, year = date[0], month = date[1]).value)
        self.assertTrue('crtMonthSalesList' in resp.context)
        