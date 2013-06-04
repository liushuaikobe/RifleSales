from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from login.models import Salesman

def index(request):
    return render_to_response('index.html', None, RequestContext(request))

def login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        pwd = request.POST.get('pwd')
        if uname and pwd:
            try:
                tmp = Salesman.objects.get(user_name=uname, pass_word=pwd)
                request.session['user_name'] = tmp.user_name
                request.session['real_name'] = tmp.real_name
                return HttpResponseRedirect('/checkin/')
            except Salesman.DoesNotExist:
                error = "please input the correct username and the password."
        else:
            error = "please input your user name and the password."
        return render_to_response('index.html', {'error':error}, RequestContext(request))
    return render_to_response('index.html', None, RequestContext(request))
