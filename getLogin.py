# -*- coding: utf-8 -*-
import base64

from threading import Thread
import time
import requests
from io import BytesIO
import http.cookiejar as cookielib
from PIL import Image
import os
import qrcode

import uuid
from datetime import datetime
from fake_useragent import UserAgent
ua = UserAgent()
random_user_agent = ua.random
requests.packages.urllib3.disable_warnings()

headers = {
    'authority': 'sso.douyin.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    # 'cookie': 'passport_csrf_token=5ffad7da4d32e03cc24f8010bd3f7356; passport_csrf_token_default=5ffad7da4d32e03cc24f8010bd3f7356; ttwid=1%7Ci3sIVxIy7lyCW05AUGaw-jXvFfGoIlSl14UrRZnLqAs%7C1696059041%7C738d03352f2f67c16293a49080061ca75ba4eede5ed825db8e4b5360987aa67f',
    'origin': 'https://www.douyin.com',
    'referer': 'https://www.douyin.com/',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}
cookies = {
    'passport_csrf_token': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'passport_csrf_token_default': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'ttwid': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
}
#为确保打开二维码还能继续运行
class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data=data
        self.qr = qrcode.QRCode(version=5, box_size=10, border=4)

    def run(self):
        
        self.qr.add_data(self.data)
        self.qr.make(fit=True)

        # 获取生成的二维码图像
        qr_image = self.qr.make_image(fill_color="black", back_color="white")

        # 打印二维码
        qr_image.show()
        

#判断cookies值是否失效
# def islogin(session):
#     loginurl = "https://www.douyin.com/webcast/user/me/?aid=1128&fp=verify_ln5prqeh_A0ZKcGS7_u90V_48aO_9BeN_iICRjovsNqWY&t=1696059459306"
#     try:
#         session.cookies.load(ignore_discard=True)
#     except Exception:
#         pass
#     response = session.get(loginurl, verify=False, headers=headers)
#     if response.json()['status_code'] == 0:
#         print('Cookies值有效，无需扫码登录！')
#         return session, True
#     else:
#         print('Cookies值已经失效，请重新扫码登录！')
#         return session, False

#获取cookies值
def dylogin():
    #将获取的cookies值进行文本保存
    if not os.path.exists('cookies.txt'):
        with open("cookies.txt", 'w') as f:
            f.write("")
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
    # session, status = islogin(session)
    # if not status:
    loginurl = "https://sso.douyin.com/get_qrcode/?aid=10006&service=https:%2F%2Fwww.douyin.com%2Fpay&t=1696059062596"
    urldata = session.get(loginurl,cookies=cookies, headers=headers).json()
    t = showpng(urldata['data']['qrcode_index_url'])
    t.start()
    token = urldata['data']['token']
    tokenurl = f'https://sso.douyin.com/check_qrconnect/?aid=10006&token={token}&service=https:%2F%2Fwww.douyin.com%2Fpay&t=1696059071774'
    while 1:
        qrcodedata = session.get(tokenurl, cookies=cookies,headers=headers).json()

        if qrcodedata['data']['status'] == "1":
            print('二维码未失效，请扫码！')
        elif qrcodedata['data']['status'] == "2":
            print('已扫码，请确认！')
        elif qrcodedata['data']['status'] == "5":
            print('二维码已失效，请重新运行！')
        if qrcodedata['data']['status'] == "3":
            print('已确认，登录成功！')
            session.get(qrcodedata['data']['redirect_url'], headers=headers)
            userInfo=session.get("https://www.douyin.com/webcast/user/me/?aid=1128&fp=verify_ln5prqeh_A0ZKcGS7_u90V_48aO_9BeN_iICRjovsNqWY&t=1696065224838", headers=headers).json().get("data")
            
            print(f"当前账号用户名：{userInfo.get('nickname')}，抖音号：{userInfo.get('display_id')}，常登录地：{userInfo.get('location_city')}")
            print("======================================================")

            ck=""
            for i in session.cookies:
                ck+=i.name+"="+i.value+";"
         
            # 打开文件并写入文本内容
            with open(f"./cookies/{userInfo.get('display_id')}.txt", "w") as file:
                file.write(ck)
            session.cookies.save()
            input(f"当前账号Cookies已存放在【cookies/{userInfo.get('display_id')}.txt】文件中，请及时查看！")
            print("======================================================")
            break
        time.sleep(5)
        
    return session



def decode_expiry_string(mac_address,expiry_string):
        expiry_bytes = base64.b64decode(expiry_string.encode('utf-8'))
        decoded_string = expiry_bytes.decode('utf-8')
        unique_id, expiry_timestamp = decoded_string.split("#")
        dt = datetime.fromtimestamp(int(float(expiry_timestamp)))

# 格式化日期和时间
        formatted_datetime = dt.strftime('%Y-%m-%d %H:%M:%S')
        if str(unique_id) == str(mac_address):
            expiry_date = datetime.fromtimestamp(float(expiry_timestamp))
            current_date = datetime.now()
            # print(unique_id,expiry_timestamp)
            if current_date <= expiry_date:
                return formatted_datetime
        return False

def getMac():
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 48, 8)])
    unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, mac_address)
    return unique_id

def checkKeys(mac_address):
    keyString=""
    with open('keys.txt', 'r',errors='ignore') as file:
            line = file.readline()
            # 读取第一行内容
            keyString=line
            return decode_expiry_string(mac_address,keyString)

def main():
    print("======================================================")
    mac_address=getMac()
    print("当前物理地址：",mac_address)
    flag=checkKeys(mac_address)
    if flag:
        print("本机到期时间：",flag)
        print("======================================================")
        dylogin()
    else:
        print("请先联系管理员激活再使用")
if __name__ == '__main__':
    main()

