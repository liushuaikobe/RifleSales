from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum

from login.models import Salesman, Administrator
from checkindata.models import Sales, Merchandise
from viewdata.models import Commission
from checkindata.views import getCurrentDate, calcCommission, haveFinished

import checkindata.views

# the data template need can get from session

def viewcurrent(request):
    crtSalesman = getSalesManFromSession(request)
    if not crtSalesman:
        return HttpResponseRedirect('/')
    date = getCurrentDate()
    # get the commission of current month until now
    commissionVal = getCurrentMonthCommission(crtSalesman, date)
    # create a sales list of current month
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
    # meta list
    meta = {'crtMonthSalesList':crtMonthSalesList, 'user_name' : crtSalesman.real_name, 'year' : date[0], 'month' : date[1], 'day' : date[2], 'commissionVal' : commissionVal}
    # return
    return render_to_response('viewcurrent.html', meta, RequestContext(request))

def viewhistory(request):
    crtSalesman = getSalesManFromSession(request)
    if not crtSalesman:
        return HttpResponseRedirect('/')
    year = request.GET.get('year')
    month = request.GET.get('month')
    date = getCurrentDate()
    if year and month:
        date = (year, month, year[2])
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
    meta = {'yearList' : getAvaliableYearList(crtSalesman), \
            'monthList' : getAvaliableMonthList(crtSalesman), \
            'user_name' : crtSalesman.real_name, \
            'crtViewYear' : date[0], \
            'crtViewMonth' : date[1], \
            'crtMonthSalesList' : crtMonthSalesList, \
            'commissionList' : getEachMonthCommissionListOfOneYear(crtSalesman, date), \
            'locks' : getEachMonthSalesCountListOfOneYear(crtSalesman, date, checkindata.views.LOCK_NAME), \
            'stocks' : getEachMonthSalesCountListOfOneYear(crtSalesman, date, checkindata.views.STOCK_NAME), \
            'barrels' : getEachMonthSalesCountListOfOneYear(crtSalesman, date, checkindata.views.BARREL_NAME)}
    return render_to_response('viewhistory.html', meta, RequestContext(request))

def gunaddsalesman(request):
    crtAdmin = getAdministratorFromSession(request)
    if not crtAdmin:
        return HttpResponseRedirect('/')
    meta = {'user_name' : crtAdmin.real_name}
    if request.method == 'POST':
        errorMsg = handleAddSalesman(request)
        if errorMsg:
            meta['errorMsg'] = errorMsg
        else:
            meta['success'] = 'Add successfully.'
    return render_to_response('gunaddsalesman.html', meta, RequestContext(request))

def gunviewcurrent(request):
    crtAdmin = getAdministratorFromSession(request)
    if not crtAdmin:
        return HttpResponseRedirect('/')
    date = getCurrentDate()
    categories = [salesman.real_name for salesman in Salesman.objects.all()]
    meta = {'dataList':getGunViewCurrentFigureData(date), \
            'categories' : categories, \
            'user_name' : crtAdmin.real_name, \
            'locks' : getGunViewCurrentMerchandiseCount(date, checkindata.views.LOCK_NAME), \
            'stocks' : getGunViewCurrentMerchandiseCount(date, checkindata.views.STOCK_NAME), \
            'barrels' : getGunViewCurrentMerchandiseCount(date, checkindata.views.BARREL_NAME)}
    return render_to_response('gunviewcurrent.html', meta, RequestContext(request))

def gunviewhistory(request):
    crtAdmin = getAdministratorFromSession(request)
    if not crtAdmin:
        return HttpResponseRedirect('/')
    year = request.GET.get('year')
    date = getCurrentDate()
    if year:
        date = (year, date[1], date[2])
    meta = {'user_name' : crtAdmin.real_name, \
            'yearList' : getAllYearsList(), \
            'crtViewYear' : date[0], \
            'locks' : getSalesCountPerMonthOneYearList(date, checkindata.views.LOCK_NAME), \
            'stocks' : getSalesCountPerMonthOneYearList(date, checkindata.views.STOCK_NAME), \
            'barrels' : getSalesCountPerMonthOneYearList(date, checkindata.views.BARREL_NAME), \
            'profit' : getProfitPerMonthOneYearList(date)}
    return render_to_response('gunviewhistory.html', meta, RequestContext(request))
    
def handleAddSalesman(request):
    error = ''
    userName = request.POST.get('username')
    realName = request.POST.get('realname') 
    passWord = request.POST.get('password')
    if userName and realName and passWord:
        try:
            userName = str(userName)
            realName = str(realName)
            passWord = str(passWord)
            salesman = Salesman()
            salesman.user_name = userName
            salesman.real_name = realName
            salesman.pass_word = passWord
            salesman.save()
        except ValueError:
            error = 'Please check your data (should be a legal String).'
            return error
        except:
            error = 'Add error.Please try later.'
            return error
    else:
        error = 'Please fill in all data.'
    return error
    
    
def getSalesManFromSession(request):
    '''
    get a salesman entity from the session of current request.
    '''
    crtSalesmanUserName = request.session['user_name'] if 'user_name' in request.session else None
    crtSalesmanRealName = request.session['real_name'] if 'real_name' in request.session else None
    if crtSalesmanUserName and crtSalesmanRealName:
        try:
            return Salesman.objects.get(user_name = crtSalesmanUserName, real_name = crtSalesmanRealName)
        except Salesman.DoesNotExist:
            return None
    return None

def getAdministratorFromSession(request):
    '''
    get a salesman entity from the session of current request.
    '''
    crtAdminUserName = request.session['user_name'] if 'user_name' in request.session else None
    crtAdminRealName = request.session['real_name'] if 'real_name' in request.session else None
    if crtAdminUserName and crtAdminRealName:
        try:
            return Administrator.objects.get(user_name = crtAdminUserName, real_name = crtAdminRealName)
        except Administrator.DoesNotExist:
            return None
    return None

def getCurrentMonthSales(crtSalesman, date, merchandiseName):
    '''
    get the sales of given crtSalesman in a given month
    '''
    merchandise = Merchandise.objects.get(name = merchandiseName)
    sales = Sales.objects.filter(whosales = crtSalesman.id, saleswhat = merchandise.id, year = date[0], month = date[1]).values('location').annotate(sum = Sum('count'))
    salesLocationAndSum = {}
    for sale in sales:
        salesLocationAndSum[sale['location']] = sale['sum'] #{'Chifeng' : 34, 'Fujian' : 10}
    return salesLocationAndSum

def getCurrentMonthVisitedLocation(crtSalesman, date):
    '''
    get all locations crtSalesman has visited in give date
    '''
    locations = []
    locationDict = Sales.objects.filter(whosales = crtSalesman.id, year = date[0], month = date[1]).values('location').distinct()
    for location in locationDict:
        locations.append(location['location'])
    return locations

def getCurrentMonthCommission(crtSalesman, date):
    '''
    get the commission of given salesman in given date
    '''
    try:
        commission = Commission.objects.get(whose = crtSalesman.id, year = date[0], month = date[1])
        return commission.value
    except Commission.DoesNotExist:
        return 0
    
def getEachMonthCommissionListOfOneYear(crtSalesman, date):
    data = []
    monthList = [i + 1 for i in range(12)]
    for month in monthList:
        tmpDate = (date[0], month, date[2])
        data.append(getCurrentMonthCommission(crtSalesman, tmpDate))
    return data

def getEachMonthSalesCountListOfOneYear(crtSalesman, date, merchandiseName):
    data = []
    monthList = [i + 1 for i in range(12)]
    merchandise = Merchandise.objects.get(name = merchandiseName)
    for month in monthList:
        sumCount = Sales.objects.filter(year = date[0], month = month, saleswhat = merchandise.id, whosales = crtSalesman.id).aggregate(sum = Sum('count'))['sum']
        data.append(sumCount if sumCount else 0)    
    return data

def getAvaliableYearList(crtSalesman):
    data = []
    yearDictList = Commission.objects.filter(whose = crtSalesman.id).values('year').distinct()
    for yearDict in yearDictList:
        data.append(yearDict['year'])
    return data

def getAvaliableMonthList(crtSalesman):
    data = []
    monthDictList = Commission.objects.filter(whose = crtSalesman.id).values('month').distinct()
    for monthDict in monthDictList:
        data.append(monthDict['month'])
    return data
    
def getGunViewCurrentFigureData(date):
    data = []
    locationList = []
    salesmanList = Salesman.objects.all()
    for location in Sales.objects.values('location').distinct():
        locationList.append(location['location'])
    for location in locationList:
        dataItem = {}
        dataItem['location'] = location
        
        countList = {}
        
        lockList = []
        stockList = []
        barrelList = []
        
        for salesman in salesmanList:
            lockSalesInCrtMonth = getCurrentMonthSales(salesman, date, checkindata.views.LOCK_NAME)
            stockSalesInCrtMonth = getCurrentMonthSales(salesman, date, checkindata.views.STOCK_NAME)
            barrelSalesInCrtMonth = getCurrentMonthSales(salesman, date, checkindata.views.BARREL_NAME)
            
            lockList.append(lockSalesInCrtMonth[location] if location in lockSalesInCrtMonth else 0)
            stockList.append(stockSalesInCrtMonth[location] if location in stockSalesInCrtMonth else 0)
            barrelList.append(barrelSalesInCrtMonth[location] if location in barrelSalesInCrtMonth else 0)
            
        countList['lockList'] = lockList
        countList['stockList'] = stockList
        countList['barrelList'] = barrelList
        
        dataItem['countList'] = countList
        data.append(dataItem)
    print data
    return data

def getGunViewCurrentMerchandiseCount(date, merchandiseName):
    '''
    {'count' : 87, 'price' : 50, 'profit' : 50 * 87}
    '''
    data = {}
    merchandise = Merchandise.objects.get(name = merchandiseName)
    count = Sales.objects.filter(year = date[0], month = date[1], saleswhat = merchandise.id).aggregate(sum = Sum('count'))['sum']
    count = count if count else 0
    data['count'] = count
    data['price'] = merchandise.price
    data['profit'] = count * merchandise.price
    return data    

def getAllYearsList():
    '''
    return all years via a list
    '''
    data = []
    yearDict = Sales.objects.all().values('year').distinct()
    for year in yearDict:
        data.append(year['year'])
    return data 

def getSalesCountPerMonthOneYearList(date, merchandiseName):
    data = []
    monthList = [i + 1 for i in range(12)]
    merchandise = Merchandise.objects.get(name = merchandiseName)
    for month in monthList:
        sumCount = Sales.objects.filter(year = date[0], month = month, saleswhat = merchandise.id).aggregate(sum = Sum('count'))['sum']
        data.append(sumCount if sumCount else 0)
    return data

def getProfitPerMonthOneYearList(date):
    data = []
    monthList = [i + 1 for i in range(12)]
    merchandiseList = Merchandise.objects.all()
    for month in monthList:
        profit = 0
        for merchandise in merchandiseList:
            count = Sales.objects.filter(year = date[0], month = month, saleswhat = merchandise.id).aggregate(sum = Sum('count'))['sum']
            count = count if count else 0
            profit += count * merchandise.price
        data.append(profit)
    return data
    
    
    
        
    
    
    
    
    
    
    
    
    
    
    
        
