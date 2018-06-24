﻿"""
下载B站指定视频
"""


from contextlib import closing
import requests
import sys,os
import re
import json
import shutil


def make_path(p):  
    """
        判断文件夹是否存在
        存在则清空
        不存在则创建
    """
    if os.path.exists(p):       # 判断文件夹是否存在  
        shutil.rmtree(p)        # 删除文件夹  
    os.mkdir(p)                 # 创建文件夹  

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.bilibili.com'}

sess = requests.Session()  
#下载的根目录
root_dir = '.'          

def download_video(video_url, file, index):
    size = 0
    '''
        当使用requests的get下载大文件/数据时，建议使用使用stream模式。
        当把get函数的stream参数设置成False时，它会立即开始下载文件并放到内存中，如果文件过大，有可能导致内存不足。
        当把get函数的stream参数设置成True时，它不会立即开始下载，当你使用iter_content或iter_lines遍历内容或访问内容属性时才开始下载。需要注意一点：文件没有下载之前，它也需要保持连接。
        iter_content：一块一块的遍历要下载的内容
        iter_lines：一行一行的遍历要下载的内容
    '''
    session = requests.Session() 
    response = session.get(video_url, headers=headers, stream=True, verify=False)
    chunk_size = 1024 #每次1KB
    content_size = int(response.headers['content-length'])
    if response.status_code == 200:
        sys.stdout.write('第%d个片段：[文件大小]:%0.2f MB\n' % (index, content_size / 1024 / 1024))
            
        for data in response.iter_content(chunk_size = chunk_size):
            file.write(data)
            size += len(data)
            file.flush()

            sys.stdout.write('第%d个片段：[下载进度]:%.2f%%' % (index, float(size / content_size * 100)) + '\r')
            if size / content_size == 1:
                print('\n')    
    else:
        print('链接异常')    


def download_videos(dir, video_urls, video_name):
    print('正在下载 %s 到 %s 文件夹下' %(video_name, dir))
    video_name = os.path.join(dir, video_name)
    with open(video_name, 'wb') as file:
        print("共有%d个片段需要下载" %len(video_urls))
        for i, video_url in enumerate(video_urls):
            
            download_video(video_url, file, i+1)
                
def get_download_urls(arcurl):
    req = sess.get(url=arcurl, verify=False)
    pattern = '.__playinfo__=(.*)</script><script>window.__INITIAL_STATE__='
    try:
        infos = re.findall(pattern, req.text)[0]
    except:
        return '',''
    json_ = json.loads(infos)
    durl = json_['durl']
    """
        不知道是什么原因
        每一个视频的最后一个片段的url都无法下载视频
        经试验将'mirroross'替换成'mirrorcos'后可下载
    """
    urls = [url['url'].replace('mirroross', 'mirrorcos') for url in durl]
    return urls

def get_page_count(url):
    """
        获取一个视频的页数
    """
    req=sess.get(url)
    pattern = '\"pages\":(\[.*\]),\"embedPlayer\"'
    try:
        infos = re.findall(pattern, req.text)[0]
    except:
        pass
    json_ = json.loads(infos)
    title_pages = dict([(page['part'],page['page']) for page in json_])
    title = re.findall('<title .*>(.*)</title>', req.text)[0]
    return title_pages, title

def download_all(aid):
    """
        给定一个视频号，下载所有的视频
    """
    url = 'https://www.bilibili.com/video/av%s'%aid
    title_pages, title = get_page_count(url)
    dir = os.path.join(root_dir, title)
    make_path(dir)
    print('创建文件夹 %s 成功' %dir)
    for title,page in title_pages.items():
        video_url = 'https://www.bilibili.com/video/av6538245/?p=%d' %page
        urls = get_download_urls(video_url)
        download_videos(dir, urls, '%s.flv' %title)
    
aid = '6538245'
download_all(aid)

#dir = '.'
#video_urls = ['http://upos-hz-mirrorcos.acgvideo.com/upgcxcode/87/67/10636787/10636787-3-32.flv?e=ig8euxZM2rNcNbNzhWNVhoMM7bNMhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1529821499&dynamic=1&gen=playurl&oi=2001726840&os=oss&platform=pc&rate=231200&trid=bc737d2be509444d8b74a7f0fa0b9831&uipk=5&uipv=5&um_deadline=1529821499&um_sign=2e2f1e835bbb495cbc2029d6f6ab92d9&upsig=a0a4a8a2d6440e694ca32e4a80cedf67']
#backup_urls = video_urls
#video_name = 'ss.flv'
#download_videos(dir, video_urls, backup_urls, video_name)