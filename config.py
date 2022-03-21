import os

TG_TOKEN = os.environ['TG_STATION_VIDEO_SEND_BOT_TOKEN']

ADMIN_IDS = list(map(lambda x: int(x), os.environ['ADMIN_IDS'].split())) if os.environ.get('ADMIN_IDS') else []