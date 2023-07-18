from time import sleep
from onvif import ONVIFCamera
from multiprocessing import Process, Queue
import zeep
import cv2

ip = '192.168.1.125'
username = 'admin'
password = 'a12345678'

mycam = ONVIFCamera(ip, 80, username, password)
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0]


def real_track(_label):
    print('正在real_track中')
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    request = ptz.create_type('ContinuousMove')
    if request.Velocity is None:
        request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
    request.ProfileToken = media_profile.token

    requestr = ptz.create_type('RelativeMove')
    requestr.ProfileToken = media_profile.token
    if requestr.Translation is None:
        requestr.Translation = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        requestr.Translation.PanTilt.space = ptz_configuration_options.Spaces.RelativePanTiltTranslationSpace[0].URI
        requestr.Translation.Zoom.space = ptz_configuration_options.Spaces.RelativeZoomTranslationSpace[0].URI
    if requestr.Speed is None:
        requestr.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        requestr.Speed.PanTilt.space = ptz_configuration_options.Spaces.RelativePanTiltTranslationSpace[0].URI
        requestr.Speed.Zoom.space = ptz_configuration_options.Spaces.RelativeZoomTranslationSpace[0].URI

    x, y = (_label[0] + _label[2]) / 2, (_label[1] + _label[3]) / 2
    box_height = _label[3] - _label[1]
    offset_x = x - 1280 / 2
    offset_y = y - 720 / 2
    offset_z = box_height / 720
    speed_x = offset_x / 1280
    speed_y = offset_y / -540

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
    print(speed_x, speed_y)
    request.Velocity.Zoom = 0
    ptz.ContinuousMove(request)

    if 590 < x < 690 and 310 < y < 410:
        if box_height > 150 or box_height < 100:
            print(667)
            if box_height > 80:
                requestr.Translation.Zoom = float(-0.01)
            elif box_height < 60:
                requestr.Translation.Zoom = float(0.01)
            else:
                requestr.Translation.Zoom = float(0)
        requestr.Translation.PanTilt.x = float(0)
        requestr.Translation.PanTilt.y = float(0)
        requestr.Speed.PanTilt.x = 0
        requestr.Speed.PanTilt.y = 0
        requestr.Speed.Zoom = 0.1
        ptz.RelativeMove(requestr)