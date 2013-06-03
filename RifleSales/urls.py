from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from login.views import index, login
from viewdata.views import viewcurrent, viewhistory
from checkindata.views import checkin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', index),
    url(r'^login/$', login),

    url(r'^checkin/$', checkin),
    url(r'^viewcurrent/$', viewcurrent),
    url(r'^viewhistory/$', viewhistory),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
