#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#   Author : SoSo

from functools import wraps
from django.http import HttpResponseRedirect
import base64, hmac, hashlib, json
from . import openid
from django.http import HttpResponse


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request = args[0]
        if request.session.get("user_email") is None:
            # 这里默认登录后跳转回原来页面，可以再此更改你想要跳转的固定页面
            index_url = "http://" + request.get_host() + "/"
            location, openid_sig_key = openid.redirect_url(index_url, index_url)
            # 这里返回的一个是login页面， 另一个是校验用的key
            request.session["openid_sig_key"] = openid_sig_key
            return HttpResponseRedirect(location)
        else:
            return f(*args, **kwargs)
    return decorated


def login_callback(request):
    OPENID_RESPONSE = dict(request.GET)
    SIGNED_CONTENT = []

    for k in OPENID_RESPONSE["openid.signed"][0].split(","):
        response_data = OPENID_RESPONSE["openid.%s" % k]
        SIGNED_CONTENT.append("%s:%s\n" % (k, response_data[0]))
    SIGNED_CONTENT = "".join(SIGNED_CONTENT).encode("UTF-8")

    SIGNED_CONTENT_SIG = base64.b64encode(
            hmac.new(base64.b64decode(request.session.get("openid_sig_key", "")),
            SIGNED_CONTENT, hashlib.sha256).digest())

    if str(SIGNED_CONTENT_SIG, encoding="utf-8") != OPENID_RESPONSE["openid.sig"][0]:
        return HttpResponse(json.dumps({"success": False, "msg": "500 OpenID Error."}), content_type="application/json")

    request.session.pop("openid_sig_key", None)
    next_url = OPENID_RESPONSE.get("next")[0]

    email = OPENID_RESPONSE.get("openid.sreg.email")[0]
    fullname = OPENID_RESPONSE.get("openid.sreg.fullname")[0]
    nickname = OPENID_RESPONSE.get("openid.sreg.nickname")[0]

    request.session["user_email"] = email
    request.session["user_fullname"] = fullname
    request.session["user_nickname"] = nickname

    return HttpResponseRedirect(next_url)


def logout_callback(request):
    request.session["user_email"] = None
    request.session["user_fullname"] = None
    request.session["user_nickname"] = None
    # 在这里可以修改你想调回去的page
    index_url = "http://" + request.get_host() + "/"
    return HttpResponseRedirect(index_url)


if __name__ == "__main__":
    print("login_util")
