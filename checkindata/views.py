from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def checkin(request):
    return render_to_response('checkin.html', None, RequestContext(request))