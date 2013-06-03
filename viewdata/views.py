from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

# the data template need can get from session

def viewcurrent(request):
    return render_to_response('viewcurrent.html', None, RequestContext(request))

def viewhistory(request):
    return render_to_response('viewhistory.html', None, RequestContext(request))