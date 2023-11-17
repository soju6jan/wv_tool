import functools
import re
from urllib.parse import urlparse
from unittest.mock import patch

import requests

from framework.init_main import Framework
from wv_tool.setup import P as PLUGIN
from wv_tool import WVDownloader


FRAMEWORK = Framework.get_instance()
PTN_WAVVE_URL = re.compile(r'wavve\.com')
PTN_AMPERSAND = re.compile(r'&(?!#38;)')


def patch_wrapper(f: callable, target: str, inject: callable) -> callable:
    @functools.wraps(f)
    def wrap(*args, **kwds):
        with patch(target, inject):
            return f(*args, **kwds)
    return wrap


def check_status_code(f: callable) -> callable:
    @functools.wraps(f)
    def wrap(*args, **kwds) -> requests.Response:
        response = f(*args, **kwds)
        if not str(response.status_code).startswith('2'):
            PLUGIN.logger.error(f'code: {response.status_code}, content: {response.text}')
        return response
    return wrap


def get_wavve_proxy() -> dict:
    '''
    프록시 설정값 가져오기
    '''
    proxies = {'http': None, 'https': None}
    support_site = FRAMEWORK.PluginManager.get_plugin_instance('support_site')
    use_proxy = support_site.ModelSetting.get_bool('site_wavve_use_proxy')
    proxy_url = support_site.ModelSetting.get('site_wavve_proxy_url')
    if use_proxy and proxy_url:
        proxies['http'] = proxy_url
        proxies['https'] = proxy_url
    return proxies


def start_wrapper(f: callable) -> callable:
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        '''
        헤더의 Host 주소를 요청 주소와 일치시킴
        '''
        self = args[0]
        mpd_url = urlparse(self.mpd_url)
        match = PTN_WAVVE_URL.search(mpd_url.netloc)
        if match and 'Host' in self.mpd_headers:
            self.mpd_headers['Host'] = mpd_url.netloc
        return f(*args, **kwargs)
    return wrap
WVDownloader.start = start_wrapper(WVDownloader.start)


@check_status_code
def patch_get_mpd_requests_get(*args, **kwds) -> requests.Response:
    '''
    mpd 요청시 프록시 적용 및 xml의 ampersand(&)를 escape 처리
    '''
    response = requests.request('GET', *args, **kwds, proxies=get_wavve_proxy())
    if response.text.startswith('<?xml'):
        response._content = bytes(
            PTN_AMPERSAND.sub('&#38;', response.text),
            response.encoding if response.encoding else 'utf-8')
    return response
WVDownloader.get_mpd = patch_wrapper(WVDownloader.get_mpd, 'requests.get', patch_get_mpd_requests_get)


@check_status_code
def patch_do_make_key_requests_post(*args, **kwds) -> requests.Response:
    '''
    라이센스 키 요청시 프록시 적용 및 헤더값 추가
    소스 암호화로 인해 임시방편으로 request시 새로운 헤더값 적용
    '''
    headers = kwds.get('headers')
    if headers:
        headers['license-token'] = headers.get('pallycon-customdata')
    response = requests.request('POST', *args, **kwds, proxies=get_wavve_proxy())
    return response
WVDownloader.do_make_key = patch_wrapper(WVDownloader.do_make_key, 'requests.post', patch_do_make_key_requests_post)
