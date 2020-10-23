#!/usr/bin/env python
# encoding: utf-8
'''
@author: zhaolong
@project : xuexi
@file: urls.py
@time: 2020/10/22 10:40
#@ide    : PyCharm
@desc:
'''
from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from polls.openid_utils import login_util

from . import views


urlpatterns = [
    path('', views.index, name='index'),

]