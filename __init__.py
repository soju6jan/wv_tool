import os
import platform
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

os.system("pip install protobuf==3.20")

try:
    import xmltodict
except:
    os.system("pip install xmltodict")

plugin_info = {
    'version' : '1.0.0.0',
    'name' : __name__.split('.')[0],
    'category' : 'library',
    'developer' : 'soju6jan',
    'description' : 'DRM 영상 다운로드에 사용하는 라이브러리.<br>외부 유출 금지',
    'home' : f'https://github.com/soju6jan',
    'policy_level' : 5,
}

try:
    from Cryptodome.Random import get_random_bytes
except:
    os.system('pip install pycryptodomex')

try:
    if platform.system() == 'Linux':
        bin_path = os.path.join(os.path.dirname(__file__), 'bin', 'Linux')
        os.system(f"chmod 777 -R {bin_path}")
except:
    pass        


from support import SupportSC

WVDownloader = SupportSC.load_module_f(__file__, 'downloader').WVDownloader
#Ffmpeg = SupportSC.load_module_f(__file__, 'ffmpeg').Ffmpeg
#WVDecryptManager = SupportSC.load_module_f(__file__, 'manager').WVDecryptManager
#WVTool = SupportSC.load_module_f(__file__, 'tool').WVTool
#from .downloader import WVDownloader
from .manager import WVDecryptManager
from .tool import WVTool

"""
python -m flaskfarm.cli.code_encode --source C:\work\FlaskFarm\data\LOADING2\wv_tool\lib\pywidevine\cdm

python -m flaskfarm.cli.code_encode --source C:\work\FlaskFarm\data\LOADING2\wv_tool\downloader.py
"""
