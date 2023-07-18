from time import sleep
from onvif import ONVIFCamera
from multiprocessing import Process, Queue
import zeep
import cv2

global XMAX, XMIN, YMAX, YMIN
ip = '192.168.1.125'
username = 'admin'
password = 'a12345678'

mycam = ONVIFCamera(ip, 80, username, password)
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0]


def video_capture(queue):
    # 打开摄像头
    cap = cv2.VideoCapture(get_stream_uri(ip, username, password))
    while True:
        # 读取视频帧
        ret, frame = cap.read()
        if not ret:
            break
        # 将视频帧放入队列
        while queue.qsize()>1:
            queue.get()

        queue.put(frame)
    # 释放摄像头
    cap.release()


def cv2Imshow(queue):
    while True:
        # 从队列中获取视频帧
        frame = queue.get()
        # 在此处可以进行帧处理或显示
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # 关闭窗口
    cv2.destroyAllWindows()


# 获取主媒体配置的媒体流URI
def get_stream_uri(device_ip, username, password):
    stream_uri = media.GetStreamUri(
        {'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
         'ProfileToken': media_profile.token})
    if stream_uri is None:
        print("无法获取视频流URI")
        return None
    return f'rtsp://{username}:{password}@' + stream_uri.Uri[7:]


def zeep_pythonvalue(xmlvalue):
    return xmlvalue


# 巡航
def move(request, _AbsoluteMove):
    request.Velocity.PanTilt.x = 0.3
    request.Velocity.PanTilt.y = 0.3
    ptz.AbsoluteMove(_AbsoluteMove)
    print('init...')
    while 1:
        if ptz.GetStatus({'ProfileToken': media_profile.token}).Position.PanTilt.y == 1:
            break
    print('move...')
    while 1:
        request.Velocity.PanTilt.y = -0.3
        ptz.ContinuousMove(request)
        while 1:
            if ptz.GetStatus({'ProfileToken': media_profile.token}).Position.PanTilt.y <= 0.4:
                break
        request.Velocity.PanTilt.y = 0.3
        ptz.ContinuousMove(request)
        while 1:
            if ptz.GetStatus({'ProfileToken': media_profile.token}).Position.PanTilt.y == 1:
                break


def real_move():
    # # 创建一个队列用于存储视频帧
    # queue = Queue()
    # # 创建一个进程用于视频捕获
    # capture_process = Process(target=video_capture, args=(queue,))
    # # 启动视频捕获进程
    # capture_process.start()
    # # 创建一个进程用于imshow
    # cv2Imshow_process = Process(target=cv2Imshow, args=(queue,))
    # # 启动imshow进程
    # cv2Imshow_process.start()

    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    request = ptz.create_type('ContinuousMove')
    print(request)
    request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})

    if request.Velocity is None:
        request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
    # 云台最大坐标
    XMAX = 1
    XMIN = -1
    YMAX = 1
    YMIN = -1

    _AbsoluteMove = ptz.create_type('AbsoluteMove')
    _AbsoluteMove.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})
    _AbsoluteMove.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    _AbsoluteMove.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position

    _AbsoluteMove.Position.PanTilt.x = 0
    _AbsoluteMove.Speed.PanTilt.x = 6
    print(type(_AbsoluteMove.Position.PanTilt.y))
    _AbsoluteMove.Position.PanTilt.y = 1
    print(type(_AbsoluteMove.Position.PanTilt.y))
    _AbsoluteMove.Speed.PanTilt.y = 6

    _AbsoluteMove.Position.Zoom = 0
    _AbsoluteMove.Speed.Zoom = 6
    # 开始巡航
    move(request, _AbsoluteMove)
