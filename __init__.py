import os
import platform
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

os.system("pip install protobuf==3.20")

try:
    import xmltodict
except:
    os.system("pip install xmltodict")

try:
    from Cryptodome.Random import get_random_bytes
except:
    os.system('pip install pycryptodomex')

try:
    folder = None
    if platform.machine() == 'aarch64':
        '''
        arm64 환경일 경우 실행권한 부여
        '''
        folder = 'LinuxArm'
    elif platform.system() == 'Linux':
        folder = 'Linux'

    if folder:
        bin_path = os.path.join(os.path.dirname(__file__), 'bin', folder)
        os.system(f"chmod 777 -R {bin_path}")
except:
    pass

from .manager import WVDecryptManager
from .tool import WVTool

DEFINE_DEV = False

if DEFINE_DEV and os.path.exists(os.path.join(os.path.dirname(__file__), 'downloader.py')):
    import downloader
    WVDownloader = downloader.WVDownloader
else:
    from support import SupportSC

    downloader = SupportSC.load_module_f(__file__, 'downloader')
    WVDownloader = downloader.WVDownloader

import functools
import re
from urllib.parse import urlparse

def hook_request(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        response = f(*args, **kwargs)
        url = urlparse(args[0])
        match = re.search(r'wavve\.com', url.netloc)
        if match and response.text.startswith('<?xml'):
            '''
            xml 내용 중에 escape 처리되지 않은 ampersand가 있을 경우 처리
            '''
            response._content = bytes(
                re.sub(r'&(?!#38;)', '&#38;', response.text),
                response.encoding if response.encoding else 'utf-8')
        return response
    return wrap
downloader.requests.get = hook_request(downloader.requests.get)

def hook_start(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        self = args[0]
        mpd_url = urlparse(self.mpd_url)
        match = re.search(r'wavve\.com', mpd_url.netloc)
        if match and 'Host' in self.mpd_headers:
            '''
            요청 주소와 헤더의 Host 주소가 다를 경우 수정
            '''
            self.mpd_headers['Host'] = mpd_url.netloc
        return f(*args, **kwargs)
    return wrap
WVDownloader.start = hook_start(WVDownloader.start)
