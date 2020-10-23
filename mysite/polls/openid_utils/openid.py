#! /usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.parse import urlencode


def redirect_url(root_url, next_url):
    # Step 1
    # 1. 第一步进行关联（associate）操作
    # 2. openid.session_type为DH-SHA1, DH-SHA256, no-encryption
    # 3. 使用DH主要是为了在不安全通道中交换密钥，由于我们的服务是走https的，
    # 4. 所以这里使用了no-encryption
    # 5. 即发起关联只需要以HTTP POST的方式向OpenID Server提交如下固定数据
    associate_data = {
        'openid.mode': 'associate',
        'openid.assoc_type': 'HMAC-SHA256',     # OpenID消息签名算法，or HAMC-SHA1
        'openid.session_type': 'no-encryption',
    }
    
    associate_data = urlencode(associate_data).encode(encoding='UTF8')
    assoc_dict = {}
    # 直接发起关联请求，主要是因为对于网易来说，我们只有https://login.netease.com/openid/这个服务
    # 并且，我们已经明确知道他的URL是https://login.netease.com/openid/，再进行Discovery多此一举
    assoc_resp = urlopen('https://login.netease.com/openid/', associate_data)
    # OpenID Server会以行为单位，分别换回如下内容：
    # assoc_handle:{HMAC-SHA256}{5279ff11}{w6nbEA==}
    # expires_in:86400
    # mac_key:g5PWpAb+pbwuTTGDt+95tWKRxN5RAhxDjpqHGwZ2OWw=
    # assoc_type:HMAC-SHA256
    # 这些值需要存储在session或者其它地方，当用户跳转回后，需要使用这些数据校验签名
    for line in assoc_resp.readlines():
        line = line.strip()
        if not line:
            continue
        line = str(line, encoding="utf-8")
        k, v = line.split(":")
        assoc_dict[k] = v
    
    # Step 2
    # 构造重定向URL，发起请求认证
    # 已经associate完成，构造checkid_setup的内容（请求认证）
    redirect_data = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',    # 固定字符串
        'openid.mode': 'checkid_setup',  # 固定字符串
        'openid.assoc_handle': assoc_dict['assoc_handle'],  # 第一步获取的assoc_handle值
        # 如果想偷懒，可以不做associate操作，直接将openid_assoc_handle设置为空
        # 这种情况下，OpenID Server会自动为你生成一个新的assoc_handle，你需要通过check_authentication进行数据校验
        # 'openid.assoc_handle' : None,
        'openid.return_to': root_url + 'login_callback?' + urlencode({'next': next_url}),  # 当用户在OpenID Server登录成功后，你希望它跳转回来的地址
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',  # 固定字符串
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',    # 固定字符串
        'openid.realm': root_url,   # 声明你的身份（站点URL），通常这个URL要能覆盖openid.return_to
        'openid.ns.sreg': 'http://openid.net/extensions/sreg/1.1',  # 固定字符串
        # fullname为中文，如果您的环境有中文编码困扰，可以不要
        'openid.sreg.required': "nickname,email,fullname",  # 三个可以全部要求获取，或者只要求一个
    }
    redirect_data = urlencode(redirect_data)

    # 实际应用中，需要交由浏览器进行Redirect的URL，用户在这里完成交互认证
    return "https://login.netease.com/openid/?" + redirect_data, assoc_dict['mac_key']


def check_authentication(request, idp="https://login.netease.com/openid/"):
    ''' check_authentication communication: FIXME(ssx) not used '''
    check_auth = {}
    is_valid_map = {
        'false': False,
        'true': True,
    }
    
    request.update({'openid.mode': 'check_authentication'})
    authentication_data = urlencode(request).encode(encoding='UTF8')
    auth_resp = urlopen(idp, authentication_data)
    
    for line in auth_resp.readlines():
        line = line.strip()
        if not line:
            continue
        k, v = line.split(":", 1)
        check_auth[k] = v

    is_valid = check_auth.get('is_valid', 'false')
    return is_valid_map[is_valid]
