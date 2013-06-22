from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum

from login.models import Salesman
from viewdata.models import Commission
from checkindata.models import Merchandise, Sales

import time, viewdata.views

MAX_LOCKS = 70
MAX_STOCKS = 80
MAX_BARRELS = 90

LOCK_NAME = 'lock'
STOCK_NAME = 'stock'
BARREL_NAME = 'barrel'

def checkin(request):
    crtSalesmanUserName = request.session['user_name'] if 'user_name' in request.session else None
    crtSalesmanRealName = request.session['real_name'] if 'real_name' in request.session else None
    error = False
    if crtSalesmanUserName and crtSalesmanRealName:
        try:
            crtSalesman = Salesman.objects.get(user_name = crtSalesmanUserName, real_name = crtSalesmanRealName)
            allMerchandise = Merchandise.objects.all()
            date = getCurrentDate()
            meta = {'user_name':crtSalesmanRealName, \
                    'year':date[0], \
                    'month':date[1], \
                    'day':date[2], \
                    'allMerchandise':allMerchandise, \
                    'haveFinished' : haveFinished(crtSalesman, date)}
            print getOnesBalance(crtSalesman, date)
            if request.method == 'POST':
                errorMsg = handleCheckinData(request, crtSalesman, date)
                if errorMsg:
                    meta['errorMsg'] = errorMsg
                else:
                    meta['success'] = 'post successfully.'
            meta = dict(meta, **getOnesBalance(crtSalesman, date))
        except Salesman.DoesNotExist:
            error = True
        except Exception, e:
            error = True
            print e
    else:
        error = True
    if not error:        
        return render_to_response('checkin.html', meta, RequestContext(request))
    else:
        return HttpResponseRedirect('/')
    

def handleCheckinData(request, crtSalesman, date):
    error = ''
    location = request.POST.get('location')
    merchandise = request.POST.get('merchandise')
    quantity = request.POST.get('quantity')
    if location and merchandise and quantity:
        try:
            quantity = int(quantity)
            merchandise = Merchandise.objects.get(name = merchandise)
            
            balance = getOnesBalance(crtSalesman, date)
            if merchandise.name in balance:
                if quantity > balance[merchandise.name]:
                    error = 'Your %s have only %s left, but you want to sale %s.' % (merchandise.name, str(balance[merchandise.name]), str(quantity))
                    return error
            
            sales = Sales()
            sales.whosales = crtSalesman
            sales.saleswhat = merchandise
            sales.year = date[0]
            sales.month = date[1]
            sales.day = date[2]
            sales.location = location
            sales.count = quantity
            sales.save()
            calcCommission(crtSalesman, date, False)
        except ValueError:
            error = 'please input a positive integer.'
            return error
        except Merchandise.DoesNotExist:
            error = 'please correct the name of merchandise.'
            return error
        except:
            error = 'Post error.Please try later.'
            return error
    else:
        error = 'Please fill in all data.'
    return error
    
def getOnesBalance(salesman, date):
    '''get one's balance of date month.'''
    global MAX_LOCKS, MAX_STOCKS, MAX_BARRELS
    global LOCK_NAME, STOCK_NAME, BARREL_NAME
    locksId = Merchandise.objects.get(name = LOCK_NAME).id
    stockId = Merchandise.objects.get(name = STOCK_NAME).id
    barrelId = Merchandise.objects.get(name = BARREL_NAME).id
    haveSoldLocks = Sales.objects.filter(whosales = salesman.id, saleswhat = locksId, year = date[0], month = date[1]).aggregate(Sum('count'))['count__sum']
    haveSoldStocks = Sales.objects.filter(whosales = salesman.id, saleswhat = stockId, year = date[0], month = date[1]).aggregate(Sum('count'))['count__sum']
    haveSoldBarrels = Sales.objects.filter(whosales = salesman.id, saleswhat = barrelId, year = date[0], month = date[1]).aggregate(Sum('count'))['count__sum']
    haveSoldLocks = haveSoldLocks if haveSoldLocks else 0
    haveSoldStocks = haveSoldStocks if haveSoldStocks else 0
    haveSoldBarrels = haveSoldBarrels if haveSoldBarrels else 0
    return {LOCK_NAME : MAX_LOCKS - haveSoldLocks, STOCK_NAME : MAX_STOCKS - haveSoldStocks, BARREL_NAME : MAX_BARRELS - haveSoldBarrels}
    
def getCurrentDate():
    '''get the current year, month, day'''
    tmp = time.localtime(time.time())
    return tmp.tm_year, tmp.tm_mon, tmp.tm_mday

def calcCommission(crtSalesman, date, isFinal):
    '''calculate the commission for a salesman'''
    allSales = Sales.objects.filter(whosales = crtSalesman.id, year = date[0], month = date[1])
    moneySum = 0.0
    commissionVal = 0.0
    level_1 = 1000.0
    level_2 = 1800.0
    for sale in allSales:
        moneySum += sale.saleswhat.price * sale.count
    if moneySum <= level_1:
        commissionVal += moneySum * 0.1
    elif moneySum > level_2:
        commissionVal += level_1 * 0.1 + level_2 * 0.15 + (moneySum - level_1 - level_2) * 0.2
    else:
        commissionVal += level_1 * 0.1 + (moneySum - level_1) * 0.15
    try:
        commission = Commission.objects.get(whose = crtSalesman.id, year = date[0], month = date[1])
    except Commission.DoesNotExist:
        commission = Commission()
    commission.whose = crtSalesman
    commission.year = date[0]
    commission.month = date[1]
    commission.value = commissionVal
    commission.havefinished = isFinal
    commission.save()
    
def commission(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    crtSalesman = viewdata.views.getSalesManFromSession(request)
    if not crtSalesman:
        return HttpResponseRedirect('/')
    isCommission = request.POST.get('commission')
    if isCommission:
        date = getCurrentDate()
        commssion = Commission.objects.filter(whose = crtSalesman.id, year = date[0], month = date[1]).update(havefinished = True)
    return HttpResponseRedirect('/viewcurrent/')

def haveFinished(crtSalesman, date):
    return Commission.objects.get(whose = crtSalesman.id, year = date[0], month = date[1]).havefinished

def checkinDataAndroid(request):
    uname = request.GET.get('uname')
    if uname:
        try:
            crtSalesman = Salesman.objects.get(user_name = uname)
        except Salesman.DoesNotExist:
                return HttpResponse('-1')
    location = request.GET.get('location')
    count = request.GET.get('count')
    pname = request.GET.get('pname')

    date = getCurrentDate()

    if location and count and pname:
        try:
            count = int(count)
            merchandise = Merchandise.objects.get(name = pname)
            sales = Sales()
            sales.whosales = crtSalesman
            sales.saleswhat = merchandise
            sales.year = date[0]
            sales.month = date[1]
            sales.day = date[2]
            sales.location = location
            sales.count = count
            sales.save()
            return HttpResponse('1')
        except:
            return HttpResponse('-2')
    return HttpResponse('-2')

def commissionAndroid(request):
    uname = request.GET.get('uname')
    if uname:
        try:
            crtSalesman = Salesman.objects.get(user_name = uname)
        except Salesman.DoesNotExist:
                return HttpResponse('-1')
    isCommission = request.GET.get('commission')
    if isCommission:
        date = getCurrentDate()
        commssion = Commission.objects.filter(whose = crtSalesman.id, year = date[0], month = date[1]).update(havefinished = True)
        return HttpResponse('1')
    return HttpResponse('-1')