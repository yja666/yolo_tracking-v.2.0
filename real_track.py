from time import sleep
from onvif import ONVIFCamera
from multiprocessing import Process, Queue
import zeep
import cv2

ip = '192.168.1.193'
username = 'admin'
password = 'a12345678'

mycam = ONVIFCamera(ip, 80, username, password)
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0]


def real_track(_label):
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    request = ptz.create_type('ContinuousMove')
    if request.Velocity is None:
        request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
    request.ProfileToken = media_profile.token

    x, y = (_label[0] + _label[2]) / 2, (_label[1] + _label[3]) / 2
    box_height = _label[3] - _label[1]
    offset_x = x - 1280 / 2
    offset_y = y - 720 / 2
    offset_z = box_height / 720
    speed_x = offset_x / 1280
    speed_y = offset_y / -540
    ptz.Stop({'ProfileToken': media_profile.token})
    if x > 690:
        request.Velocity.PanTilt.x = speed_x
    elif x < 590:
        request.Velocity.PanTilt.x = speed_x
    else:
        request.Velocity.PanTilt.x = 0
    if y > 410:
        request.Velocity.PanTilt.y = speed_y
    elif y < 310:
        request.Velocity.PanTilt.y = speed_y
    else:
        request.Velocity.PanTilt.y = 0
    print(speed_x,speed_y)
    ptz.ContinuousMove(request)

    # _AbsoluteMove = ptz.create_type('AbsoluteMove')
    # _AbsoluteMove.ProfileToken = media_profile.token
    # _AbsoluteMove.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    # _AbsoluteMove.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    # if box_height>300:
    #     if _AbsoluteMove.Position.Zoom-0.1>=0:
    #         _AbsoluteMove.Position.Zoom -= 0.1
    #     else:
    #         _AbsoluteMove.Position.Zoom = 0
    # elif box_height<100:
    #     if _AbsoluteMove.Position.Zoom+0.05<=1:
    #         _AbsoluteMove.Position.Zoom += 0.05
    #     else:
    #         _AbsoluteMove.Position.Zoom = 1
    # AbsoluteMove.Speed.Zoom = 10
    # ptz.AbsoluteMove(_AbsoluteMove)

    # x,y=(_label[0]+_label[2])//2,(_label[1]+_label[3])//2
    # _AbsoluteMove.Speed.PanTilt.x = 10
    # _AbsoluteMove.Speed.PanTilt.y = 10
    # _AbsoluteMove.Speed.Zoom = 10
    # if x>640:
    #     if _AbsoluteMove.Position.PanTilt.x-0.2<-1:
    #         _AbsoluteMove.Position.PanTilt.x+=1.8
    #     else:
    #         _AbsoluteMove.Position.PanTilt.x -= 0.2
    # elif x<640:
    #     if _AbsoluteMove.Position.PanTilt.x+0.2 > 1:
    #         _AbsoluteMove.Position.PanTilt.x -= 1.8
    #     else:
    #         _AbsoluteMove.Position.PanTilt.x += 0.2
    # else:
    #     pass
    # if y>360:
    #     if _AbsoluteMove.Position.PanTilt.y-0.1<-1:
    #         pass
    #     else:
    #         _AbsoluteMove.Position.PanTilt.y -= 0.1
    # # 需修改
    # elif y<360:
    #     if _AbsoluteMove.Position.PanTilt.y+0.1>1:
    #         pass
    #     else:
    #         _AbsoluteMove.Position.PanTilt.y += 0.1
    # else:
    #     pass
    # ptz.AbsoluteMove(_AbsoluteMove)
    # sleep(1)
