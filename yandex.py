import requests
import json

import config


def get_session(login, password):
    # Auth and getting Session_id
    auth_data = {
        'login': login,
        'passwd': password
    }

    s = requests.Session()
    s.get("https://passport.yandex.ru/")
    s.post("https://passport.yandex.ru/passport?mode=auth&retpath=https://yandex.ru", data=auth_data)
    Session_id = s.cookies["Session_id"]

    # Getting x-csrf-token
    token = s.get('https://frontend.vh.yandex.ru/csrf_token').text

    return s, token


def get_devices(session):
    # Getting devices info
    devices_online_stats = session.get("https://quasar.yandex.ru/devices_online_stats").text
    devices = json.loads(devices_online_stats)["items"]

    return devices


def send_to_screen(session, x_csrf_token, video_url):
    devices = get_devices(session)
    if len(devices) == 1:
        device_to_send = devices[0]['id']
        device_name = devices[0]['name']
    else:
        device_to_send = devices[0]['id']
        device_name = devices[0]['name']
        # TODO: device selection here

    # Preparing request
    headers = {
        "x-csrf-token": x_csrf_token,
    }
    data = {
        "msg": {
            "provider_item_id": video_url
        },
        "device": device_to_send
    }

    if "https://www.youtube" in video_url:
        data["msg"]["player_id"] = "youtube"

    # Sending command with video to device
    res = session.post("https://yandex.ru/video/station", data=json.dumps(data), headers=headers)

    return res.text, device_name
