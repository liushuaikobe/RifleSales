from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from login.views import index, login, loginAndroid
from viewdata.views import viewcurrent, viewhistory, gunviewcurrent, gunviewhistory
from checkindata.views import checkin, commission, checkinDataAndroid

urlpatterns = patterns('',
    # index
    url(r'^$', index),
    url(r'^login/$', login),
    # login as a salesman
    url(r'^checkin/$', checkin),
    url(r'^checkin/commission/$', commission),
    url(r'^viewcurrent/$', viewcurrent),
    url(r'^viewhistory/$', viewhistory),
    # login as a administrator
    url(r'^gunviewcurrent/$', gunviewcurrent),
    url(r'^gunviewhistory/$', gunviewhistory),
    # admin site auto-create
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # url for android
    url(r'^loginAndroid/$',loginAndroid),
    url(r'^checkinAndroid/$',checkinDataAndroid),
)
