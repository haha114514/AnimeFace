from hoshino import R, Service
import re
import requests
from urllib import error
from urllib.request import urlretrieve
import random
import base64
import os
from ._util import extract_url_from_event
from io import BytesIO
from os import path
import aiohttp
from PIL import Image
from hoshino.util import DailyNumberLimiter, FreqLimiter

_nlt = DailyNumberLimiter(4)
_flt = FreqLimiter(10)
sv = Service('动漫人物', visible= True, enable_on_default= True, bundle='动漫人物', help_='''
无说明
'''.strip())

image_path = '[your file path]' # coolq 文件路径

def get_access_token():
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    data = {
        'grant_type': 'client_credentials',  # 固定值
        'client_id': '[Your API Key]',  # 在开放平台注册后所建应用的API Key
        'client_secret': '[Your Secret Key]'  # 所建应用的Secret Key
    }
    res = requests.post(url, data=data)
    res = res.json()
    #print(res)
    access_token = res['access_token']
    return access_token

@sv.on_prefix(('动漫人物'))
async def getPicList(bot, ev):
    uid = ev.user_id
    if not _nlt.check(uid):
        await bot.finish(ev, '今日已经到达上限！')

    if not _flt.check(uid):
        await bot.finish(ev, '太频繁了，请稍后再来')

    url = extract_url_from_event(ev)
    if not url:
        await bot.finish(ev, '请附带图片!')
    url = url[0]
    await bot.send(ev, '请稍等片刻~')

    _nlt.increase(uid)
    _flt.start_cd(uid, 30)
    # 将图片保存到temp.jpg并且转换为base64(默认为插件同目录)
    async with  aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            cont = await resp.read()
            b64 = (base64.b64encode(cont)).decode()
            img = Image.open(BytesIO(cont))
            img.save(path.join(path.dirname(__file__), 'temp.jpg'))
            picfile = path.join(path.dirname(__file__), 'temp.jpg')
    request_url = "https://aip.baidubce.com/rest/2.0/image-process/v1/selfie_anime"
    f = open('/[Your Plugin Path]/temp.jpg', 'rb')       # 二进制方式打开图片文件
    img = base64.b64encode(f.read()) # 图像转为base64的格式
    params = {"image":img}
    request_url = request_url + "?access_token=" + get_access_token()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    res = response.json()
    await bot.send(ev, MessageSegment.image('base64://' + res['image'])) # 让bot发送base64图片（自动转换base64到图片）
    print ("二次元变身成功")





