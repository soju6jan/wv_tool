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
        # arm64 환경일 경우 실행권한 부여
        folder = 'LinuxArm'
    elif platform.system() == 'Linux':
        folder = 'Linux'

    if folder:
        bin_path = os.path.join(os.path.dirname(__file__), 'bin', folder)
        os.system(f"chmod 777 -R {bin_path}")
except:
    pass


DEFINE_DEV = False

if DEFINE_DEV and os.path.exists(os.path.join(os.path.dirname(__file__), 'downloader.py')):
    from .downloader import WVDownloader
else:
    from support import SupportSC

    WVDownloader = SupportSC.load_module_f(__file__, 'downloader').WVDownloader
from .manager import WVDecryptManager
from .tool import WVTool

from .patches import patches