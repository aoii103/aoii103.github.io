import re
from imgcat import imgcat
import requests_html

session = requests_html.HTMLSession()
API_jsLogin = "https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN"
QR_code = "https://login.weixin.qq.com/qrcode/{}"


def get_qrcode_uid():
    resp = session.get(API_jsLogin)
    uid = re.split(r'"|";', resp.text)[1]
    print(f"uid is {uid}")
    return uid


def get_qrcode_img(uid):
    resp = session.get(QR_code.format(uid))
    return imgcat(resp.content)


uid = get_qrcode_uid()
get_qrcode_img(uid)


import execjs
import time
import base64

API_login = "https://wx.qq.com/cgi-bin/mmwebwx-bin/login"
API_check_login = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login"


def get_timestamp(reverse=False):
    if reverse:
        return execjs.eval("~new Date")
    return int(time.time() * 1e3)


def login_wait(confirm=True):
    return session.get(
        API_check_login if confirm else API_login,
        params={
            "loginicon": "true",
            "uuid": uid,
            "tip": 0 if confirm else 1,
            "r": get_timestamp(True),
            "_": get_timestamp(),
        },
        timeout=25,
    )


nums = 10
while nums > 0:
    try:
        print("等待客户端扫描，剩余次数", nums)
        res = login_wait()
        if "userAvatar" in res.text:
            print("即将打印头像")
            imgcat(base64.b64decode(re.findall("base64,(.*?)';", res.text)[0]))
            break
        nums -= 1
    except Exception as e:
        pass

print("等待客户端确认")
redirect_uri = re.findall('redirect_uri="(.*?)"', login_wait(True).text)[0]
print("即将跳转", redirect_uri)

from pprint import pprint

def get_auth_data(resp):
    return {
        key: resp.html.find(key)[0].text
        for key in ["skey", "wxsid", "wxuin", "pass_ticket", "isgrayscale"]
    }


def get_ticket():
    resp = session.get(
        redirect_uri, params={"fun": "new", "lang": "zh_CN", "_": get_timestamp()}
    )
    print("Get Ticket:")
    pprint(requests_html.requests.utils.dict_from_cookiejar(resp.cookies))
    auth_data = get_auth_data(resp)
    session.cookies.update(
        requests_html.requests.utils.cookiejar_from_dict(
            {"last_wxuin": auth_data["wxuin"]}
        )
    )
    if list(filter(lambda item: item[1], auth_data.items())):
        return auth_data


auth_data = get_ticket()
print("Get Auth_data:")
pprint(auth_data)

