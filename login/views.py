from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from login.models import salesman

def index(request):
    return render_to_response('index.html', None, RequestContext(request))

def login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        pwd = request.POST.get('pwd')
        if uname and pwd:
            try:
                tmp = salesman.objects.get(user_name = uname, pass_word = pwd)
                return render_to_response('checkin.html', {'user_name':tmp.user_name}, RequestContext(request))
            except salesman.DoesNotExist:
                error = "please input the correct username and the password."
        else:
            error = "please input your user name and the password."
        return render_to_response('index.html', {'error':error}, RequestContext(request))
    return render_to_response('index.html', None, RequestContext(request))