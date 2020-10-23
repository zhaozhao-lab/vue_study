# Create your views here.
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from polls.openid_utils.login_util import login_required


@login_required
def index(request):
    data = ({})
    data.update({
        "user_email": request.session.get("user_email"),  # email
        "user_fullname": request.session.get("user_fullname"),  # 中文名字
        "user_nickname": request.session.get("user_nickname"),  # 英文昵称
    })
    result = {"success": True}
    data.update(result)
#    return  JsonResponse({"status":0,"message":"aaaaaaaaadadsadw3dadada"})
    return redirect("http://127.0.0.1:8080/#/",)
# openid接入没有权限直接在这重定向了