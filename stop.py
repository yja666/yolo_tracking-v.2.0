from onvif import ONVIFCamera

mycam = ONVIFCamera('192.168.1.125', 80, 'admin', 'a12345678')
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0]
ptz.Stop({'ProfileToken': media_profile.token})