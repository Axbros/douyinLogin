# -*- coding: utf-8 -*-
import base64

from threading import Thread

import requests
from io import BytesIO
import http.cookiejar as cookielib
from PIL import Image
import os
from time import time,sleep

current_time=int(time()*1000)
requests.packages.urllib3.disable_warnings()

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36", 'Referer': "https://www.douyin.com/"}
session=None
#为确保打开二维码还能继续运行
class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        img = Image.open(BytesIO(self.data)) 
        img.show()

#判断cookies值是否失效
def islogin(session):
    loginurl = "https://www.douyin.com/webcast/user/me/?aid=1128&fp=verify_ln2wdy7q_LJVVvA42_8smr_4Uik_89l9_MTRqNiA5tW5C&t=1695889454665"
    try:
        session.cookies.load(ignore_discard=True)
    except Exception:
        pass
    response = session.get(loginurl, verify=False, headers=headers)
    if response.json()['status_code'] == 0:
        print('Cookies值有效，无需扫码登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False

#获取cookies值
def dylogin():
    #将获取的cookies值进行文本保存
    if not os.path.exists('cookies.txt'):
        with open("cookies.txt", 'w') as f:
            f.write("")
    global session
    session = requests.session()
    session.cookies.set("ttwid", "1%7Ci3sIVxIy7lyCW05AUGaw-jXvFfGoIlSl14UrRZnLqAs%7C1695798695%7C9441b5af3ac14fc6f0bc908d0cb85fb3f3a5367e9b7ec5b033f08cf1ee140674")
    session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
    session, status = islogin(session)
    if not status:
        loginurl = "https://sso.douyin.com/get_qrcode/?aid=10006&service=https:%2F%2Fwww.douyin.com%2Fpay&t={time}"
        urldata = session.get(loginurl, headers=headers).json()
        print(urldata['data']['qrcode'])
        # testpng = base64.b64decode()
        # t = showpng(testpng)
        # t.start()
        token = urldata['data']['token']
        tokenurl = f'https://sso.douyin.com/check_qrconnect/?aid=10006&token={token}&service=https:%2F%2Fwww.douyin.com%2Fpay%3Fis_new_connect%3D0%26is_new_user%3D0'
        while 1:
            qrcodedata = requests.get(tokenurl, headers=headers).json()
            print("res",qrcodedata)
            if qrcodedata['data']['status'] == "1":
                print('二维码未失效，请扫码！')
            elif qrcodedata['data']['status'] == "2":
                print('已扫码，请确认！')
            elif qrcodedata['data']['status'] == "5":
                print('二维码已失效，请重新运行！')
            elif qrcodedata['data']['status'] == "3":
                print('已确认，登录成功！')
                session.get(qrcodedata['data']['redirect_url'], headers=headers)
                break
   
                
            sleep(5)
        session.cookies.save()
    return session


if __name__ == '__main__':
    dylogin()

