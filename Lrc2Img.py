# -*- coding: UTF-8 -*-
import json
import requests
class NetEase():

    cookies_filename = "netease_cookies.json"

    def __init__(self):
#         super().__init__()
        self.headers = {
            'Host': 'music.163.com',
            'Connection': 'keep-alive',
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Referer': 'http://music.163.com/',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"
        }
        self.cookies = dict(appver="1.2.1", os="osx")

    def show_progress(self, response):
        content = bytes()
        total_size = response.headers.get('content-length')
        if total_size is None:

            content = response.content
            return content
        else:
            total_size = int(total_size)
            bytes_so_far = 0

            for chunk in response.iter_content():
                content += chunk
                bytes_so_far += len(chunk)
                progress = round(bytes_so_far * 1.0 / total_size * 100)
                self.signal_load_progress.emit(progress)
            return content

    def http_request(self, method, action, query=None, urlencoded=None, callback=None, timeout=1):
        headers={
            'Host': 'music.163.com',
            'Connection': 'keep-alive',
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Referer': 'http://music.163.com/',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"
        }
        cookies = dict(appver="1.2.1", os="osx")
        res = None
        if method == "GET":
            res = requests.get(action, headers=headers, cookies=cookies, timeout=timeout)
        elif method == "POST":
            res = requests.post(action, query, headers=self.headers, cookies=self.cookies, timeout=timeout)
        elif method == "POST_UPDATE":
            res = requests.post(action, query, headers=self.headers, cookies=self.cookies, timeout=timeout)
            self.cookies.update(res.cookies.get_dict())
            self.save_cookies()
        content = self.show_progress(res)
        content_str = content.decode('utf-8')
        content_dict = json.loads(content_str)
        return content_dict

    def user_playlist(self, uid):
        action = 'http://music.163.com/api/playlist/detail?id=' + str(uid)
        res_data = self.http_request('GET', action)
        return res_data



    def get_lyric_by_musicid(self, mid):

        url = 'http://music.163.com/api/song/lyric?' + 'id=' + str(mid) + '&lv=1&kv=1&tv=-1'
        return self.http_request('POST', url) #此API必须使用POST方式才能正确返回，否则提示“illegal request”

class Playlist():
    def __init__(self,uid):
        self.id=uid
    def get(self):
        uid=self.id
        import re
        music=NetEase()
        playlist = music.user_playlist(uid=uid)
        self.playlist = playlist['result']['tracks']
        self.songName = []
        self.songId = []
        self.songImg = []
        self.songLrc = []
        for song in self.playlist:
            self.songName.append(song["name"])
            self.songId.append(song["id"])
            self.songImg.append(song["album"]["blurPicUrl"])
        for songid in self.songId:
            lrc = music.get_lyric_by_musicid(mid=songid)
            lrc=lrc['lrc']['lyric']
            pat = re.compile(r'\[.*\]')
            lrc = re.sub(pat, "", lrc)
            lrc=lrc.strip()
            self.songLrc.append(lrc)
    def createImg(self):
        img=Img()
        for songName,songLrc,songImg in zip(self.songName,self.songLrc,self.songImg):
            img.save(songName,songLrc,songImg)
class Img():
    def __init__(self):

        import os
        try:
            self.Path = r'C:\Img'
            self.albumImgPath = self.Path + r'\albumImg'
            os.mkdir(self.Path)
            os.mkdir(self.albumImgPath)
        except:
            pass




        return

    def is_chinese(self,uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
        else:
            return False
    def getsize(self,lrc):

        lrc=lrc.split('\n')
        width = []
        for line in lrc:
            width.append(len(line))
        width = max(width)

        self.fontSize = 500//width-1  # 字体大小
        fontSpace = 10 # 每行间隔大小

        length=len(lrc)*(self.fontSize+fontSpace)


        return width,length




    def save(self,name,lrc,imgurl):
        from io import BytesIO
        width,length = self.getsize(lrc)
        from PIL import Image, ImageDraw, ImageFont
        isChinese=False
        for char in name:
            if self.is_chinese(char):
                isChinese=True
        if not isChinese:
            self.fontSize=int(self.fontSize*2.5)
            length*=2
        albumImgSize=500#专辑缩略图大小
        font="C:\\MFShangHei_Noncommercial-Regular.otf" #需要把字体下载到本地，并且提供其路径
        

        fontSize=self.fontSize#字体大小
        fontSpace=10#每行间隔大小
        space=10#留白
        rImg= requests.get(imgurl)
        albumImg = Image.open(BytesIO(rImg.content))
        albumImg.save(self.albumImgPath+r'\\'+name + '.bmp')
        font=ImageFont.truetype(font, fontSize)
        rSizeImg=albumImg.resize((albumImgSize,albumImgSize),resample=3)

        x=albumImgSize
        y=albumImgSize+length+space*8
        outImg=Image.new(mode='RGB', size=(x, y), color=(255, 255, 255))
        draw= ImageDraw.Draw(outImg)
        outImg.paste(rSizeImg,(0,0))

        draw.text((space*2,albumImgSize+space*2),lrc,font=font,fill=(0,0,0),spacing=fontSpace,align='left')
        # Python中字符串类型分为byte string 和 unicode string两种，'——'为中文标点byte string，需转换为unicode string
        draw.text((space*2, y-60),unicode('——', "utf-8")+name,fill=(0,0,0),font=font,align="left")
        outImg.save(self.Path+r'\\'+name+'.bmp')

        return
id=input('请输入歌单ID：')
music=Playlist(id)
music.get()
music.createImg()


           


        
    
        
 
        
      
