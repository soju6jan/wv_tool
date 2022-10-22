from support import SupportSubprocess

from .setup import *

name = 'download'

from . import WVDownloader


class ModuleDownload(PluginModuleBase):

    def __init__(self, P):
        super(ModuleDownload, self).__init__(P, 'list')
        self.name = name
        default_route_socketio_module(self, attach='/list')


    def process_menu(self, page_name, req):
        
        try:
            arg = {}

            return render_template(f'{P.package_name}_{name}_{page_name}.html', arg=arg)
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{P.package_name}/{name}/{page_name}")

    
    
    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        
        if command == 'list':
            ret = []
            for ins in WVDownloader.get_list():
                ret.append(ins.get_data())

            self.socketio_callback("status", "aaaa")
            
        return jsonify(ret)


    def process_api(self, sub, req):
        pass
    
    def plugin_load(self):
        #SupportFfmpeg.initialize(P.ModelSetting.get('ffmpeg_path'), os.path.join(F.config['path_data'], 'tmp'), self.callback_function, P.ModelSetting.get_int('max_pf_count'))
        pass

    def plugin_unload(self):
        #SupportFfmpeg.all_stop()
        pass
        
    def setting_save_after(self, change_list):
        #SupportFfmpeg.initialize(P.ModelSetting.get('ffmpeg_path'), os.path.join(F.config['path_data'], 'tmp'), self.callback_function, P.ModelSetting.get_int('max_pf_count'))
        pass
                
    

    def callback_function(self, **args):
        refresh_type = None
        if args['type'] == 'status_change':
            if args['status'] == SupportFfmpeg.Status.DOWNLOADING:
                refresh_type = 'status_change'
            elif args['status'] == SupportFfmpeg.Status.COMPLETED:
                refresh_type = 'status_change'
            elif args['status'] == SupportFfmpeg.Status.READY:
                data = {'type':'info', 'msg' : '다운로드중 Duration(%s)' % args['data']['duration_str'] + '<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                # 1번에서 리스트화면, 2번에서 추가시 1번도 추가되도록
                refresh_type = 'add'    
        elif args['type'] == 'last':
            
            if args['status'] == SupportFfmpeg.Status.WRONG_URL:
                data = {'type':'warning', 'msg' : '잘못된 URL입니다'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'
            elif args['status'] == SupportFfmpeg.Status.WRONG_DIRECTORY:
                data = {'type':'warning', 'msg' : '잘못된 디렉토리입니다.<br>' + args['data']['save_fullpath']}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'
            elif args['status'] == SupportFfmpeg.Status.ERROR or args['status'] == SupportFfmpeg.Status.EXCEPTION:
                data = {'type':'warning', 'msg' : '다운로드 시작 실패.<br>' + args['data']['save_fullpath']}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'
            elif args['status'] == SupportFfmpeg.Status.USER_STOP:
                data = {'type':'warning', 'msg' : '다운로드가 중지 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.COMPLETED:
                data = {'type':'success', 'msg' : '다운로드가 완료 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.TIME_OVER:
                data = {'type':'warning', 'msg' : '시간초과로 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.PF_STOP:
                data = {'type':'warning', 'msg' : 'PF초과로 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.FORCE_STOP:
                data = {'type':'warning', 'msg' : '강제 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'   
            elif args['status'] == SupportFfmpeg.Status.HTTP_FORBIDDEN:
                data = {'type':'warning', 'msg' : '403에러로 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'   
            elif args['status'] == SupportFfmpeg.Status.ALREADY_DOWNLOADING:
                data = {'type':'warning', 'msg' : '임시파일폴더에 파일이 있습니다.<br>' + args['data']['temp_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
        elif args['type'] == 'normal':
            if args['status'] == SupportFfmpeg.Status.DOWNLOADING:
                refresh_type = 'status'
        """
        if refresh_type is not None:
            P.logger.info(refresh_type)
            socketio.emit(refresh_type, args['data'], namespace=f'{P.package_name}/download', broadcast=True)
        """
        self.socketio_callback(refresh_type, args['data'])

        #socketio_callback.
