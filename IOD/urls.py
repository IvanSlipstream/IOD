# -*- coding: windows-1251 -*-

"""IOD URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from RFC.views import *

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add/$', add_rfc),
    url(r'^list/$', list_rfc),
    url(r'^$', user_login),
    url(r'^logout/$', user_logout),
    url(r'^profile/$', user_profile),
    url(r'^sync/$', oper_sync),
    url(r'^testrfc/$', rfc_test),
    url(r'^detail/(?P<id>.*)/$', rfc_details),
    url(r'^paper/(?P<id>.*)\.xml$', paper_rfc),
    url(r'^confirm/(?P<id>.*)/$', rfc_confirm),
    url(r'^apply/(?P<id>.*)/$', rfc_apply),
    url(r'^combined/(?P<id>.*)\.xml$', combined_rfc),
    url(r'^delete/(?P<id>.*)/$', rfc_delete),
    url(r'^edit/(?P<id>.*)/$', rfc_edit),
]
