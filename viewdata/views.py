from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum

from login.models import Salesman
from checkindata.models import Sales, Merchandise
from checkindata.views import getCurrentDate

import checkindata.views

# the data template need can get from session

def viewcurrent(request):
    global LOCK_NAME, STOCK_NAME, BARREL_NAME
    crtSalesman = getSalesManFromSession(request)
    if not crtSalesman:
        return HttpResponseRedirect('/')
    date = getCurrentDate()
    
    lockSalesInCrtMonth = getCurrentMonthSales(crtSalesman, date, checkindata.views.LOCK_NAME)
    stockSalesInCrtMonth = getCurrentMonthSales(crtSalesman, date, checkindata.views.STOCK_NAME)
    barrelSalesInCrtMonth = getCurrentMonthSales(crtSalesman, date, checkindata.views.BARREL_NAME)
    
    locationsInCrtMonth = getCurrentMonthVisitedLocation(crtSalesman, date)
    
    crtMonthSalesList = []
    
    for location in locationsInCrtMonth:
        crtMonthSales = {}
        crtMonthSales['location'] = location
        crtMonthSales['locks'] = lockSalesInCrtMonth[location] if location in lockSalesInCrtMonth else 0
        crtMonthSales['stocks'] = stockSalesInCrtMonth[location] if location in stockSalesInCrtMonth else 0
        crtMonthSales['barrels'] = barrelSalesInCrtMonth[location] if location in barrelSalesInCrtMonth else 0
        crtMonthSalesList.append(crtMonthSales)
    
    return render_to_response('viewcurrent.html', {'crtMonthSalesList':crtMonthSalesList}, RequestContext(request))

def viewhistory(request):
    return render_to_response('viewhistory.html', None, RequestContext(request))

def getSalesManFromSession(request):
    '''get a salesman entity from the session of current request.'''
    crtSalesmanUserName = request.session['user_name'] if 'user_name' in request.session else None
    crtSalesmanRealName = request.session['real_name'] if 'real_name' in request.session else None
    if crtSalesmanUserName and crtSalesmanRealName:
        try:
            return Salesman.objects.get(user_name = crtSalesmanUserName, real_name = crtSalesmanRealName)
        except Salesman.DoesNotExist:
            return None
    return None

def getCurrentMonthSales(crtSalesman, date, merchandiseName):
    '''get the sales of given crtSalesman in a given month'''
    merchandise = Merchandise.objects.get(name = merchandiseName)
    sales = Sales.objects.filter(whosales = crtSalesman.id, saleswhat = merchandise.id, year = date[0], month = date[1]).values('location').annotate(sum = Sum('count'))
    salesLocationAndSum = {}
    for sale in sales:
        salesLocationAndSum[sale['location']] = sale['sum'] #{'Chifeng' : 34, 'Fujian' : 10}
    return salesLocationAndSum

def getCurrentMonthVisitedLocation(crtSalesman, date):
    '''get all locations crtSalesman has visited in give date'''
    locations = []
    locationDict = Sales.objects.filter(whosales = crtSalesman.id, year = date[0], month = date[1]).values('location').distinct()
    for location in locationDict:
        locations.append(location['location'])
    return locations
        
