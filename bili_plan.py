import requests
import time
import json
import os
from bilibili_api import video, Verify
from lxml import etree


class BiliBili:
    def __init__(self, SESSDATA, bili_jct, DedeUserID):
        self.sessdata = SESSDATA
        self.csrf = bili_jct
        self.bili_session = requests.session()
        self.bili_session.cookies.set(name="SESSDATA", value=SESSDATA)
        self.bili_session.cookies.set(name="bili_jct", value=bili_jct)
        self.bili_session.cookies.set(name="DedeUserID", value=DedeUserID)

    def upload_video(self, title, url):
        verify = Verify(self.sessdata, self.csrf)
        # 上传视频
        filename = video.video_upload("tmp.mp4", verify=verify)
        data = {
            "copyright": 2,
            "source": url,
            "cover": None,
            "desc": "转自微博",
            "desc_format_id": 0,
            "dynamic": "",
            "interactive": 0,
            "no_reprint": 0,
            "subtitles": {
                "lan": "",
                "open": 0
            },
            "tag": "搞笑，日常",
            "tid": 22,
            "title": title,
            "videos": [
                {
                    "desc": "转自微博",
                    "filename": filename,
                    "title": "P1"
                }
            ]
        }
        # 提交投稿
        try:
            result = video.video_submit(data, verify=verify)

            # 成功的话会返回bv号和av号
            print(result)
        except Exception as e:
            print("出错了",e)

    def duplicate_check(self, title=''):
        respones = self.bili_session.get(
            'https://search.bilibili.com/all?keyword={}'.format(title))
        trees = etree.HTML(respones.text)
        li_list = trees.xpath(
            '/html/body/div[3]/div/div[2]/div/div[1]/div[2]/ul/li')
        # 没有取到任何数据说明没有撞车
        if len(li_list) == 0 or li_list == '' or li_list == None:
            return False
        for li in li_list:
            # 取视频标题
            # print(li.xpath('./a/@title'))
            if len(li.xpath('./a/@title')) != 1:
                continue
            this_title = li.xpath('./a/@title')[0]
            # 有一个视频标题全完一样说明撞车了
            if title == this_title:
                print('视频撞车了!放弃此次投稿:{}'.format(title))
                return False
        # 所有视频标题都不完全一样
        return True


class WeiBo:
    def __init__(self):
        self.bili = BiliBili(SESSDATA="ea29de59%2C1629570147%2C49191*21",
                             bili_jct="1fa558966a28d948d1782cb8133944c4", DedeUserID="1791994608")
        self.weibo_session = requests.session()
        # 微博主要分类
        self.WeiBo_video_classify = ['搞笑', '恶搞', '沙雕', '生活', '日常', '幽默', '美食']
        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Android 4.4; Mobile; rv:70.0) Gecko/70.0 Firefox/70.0'
        }
        self.weibo_api = 'https://m.weibo.cn/api/container/getIndex'
        self.get_video_info()

    def get_video_info(self):
        while True:
            for classify in self.WeiBo_video_classify:
                for page in range(0, 12):
                    params = {
                        "containerid": "100103type=72&q={}&t=0".format(classify),
                        "extparam": "title=热门视频",
                        "luicode": "10000011",
                        "lfid": "100103type=64&q={}&t=0".format(classify),
                        "page": page
                    }
                    weibo_respones = self.weibo_session.get(
                        url=self.weibo_api, params=params, headers=self.headers)
                    if weibo_respones.status_code == 418:
                        break
                    if weibo_respones.status_code == 200:
                        json = weibo_respones.json()
                        if 'msg' in json:
                            if json['msg'] == '这里还没有内容':
                                print(json['msg'])
                                time.sleep(2)
                                continue
                        try:
                            for num in range(10):
                                video_title = json['data']["cards"][0]['card_group'][num]["mblog"]['page_info']['title']
                                video_url = json['data']["cards"][0]['card_group'][num]["mblog"]['page_info']['page_url']
                                video_media = json['data']["cards"][0]['card_group'][num][
                                    "mblog"]['page_info']['media_info']['stream_url_hd']
                                print("\n\n\n", video_title, "\n", video_url,
                                      "\n", video_media, "\n")
                                if video_title != "":
                                    if self.bili.duplicate_check(video_title):
                                        self.download_video(video_media)
                                        self.bili.upload_video(
                                            video_title, video_url)
                                        os.remove("tmp.mp4")

                                time.sleep(30)
                        except IndexError:
                            print("无结果了")

    def download_video(self, url):
        v = self.weibo_session.get(url)
        f = open("tmp.mp4", "wb+")
        f.write(v.content)
        f.close()


w = WeiBo()


"""

b = BILIBILI(SESSDATA="5e0a2435%2C1616142220%2C19ff2*91",bili_jct="d06834c638accd2c8d3ce7d0e1a15308",DedeUserID="17509450")
test = b.bili_session.get("http://api.bilibili.com/x/web-interface/nav/stat")
print(test.content)
"""
