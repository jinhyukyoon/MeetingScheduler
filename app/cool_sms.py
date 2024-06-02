import time
import datetime
import uuid
import hmac
import hashlib
import platform
import json
import requests
from app.config import Config

api_key = Config.COOLSMS_API_KEY
api_secret = Config.COOLSMS_API_SECRET
protocol = 'https'
domain = 'api.coolsms.co.kr'
prefix = ''

def get_url(path):
    url = '%s://%s' % (protocol, domain)
    if prefix != '':
        url = url + prefix
    url = url + path
    return url

def unique_id():
    return str(uuid.uuid1().hex)

def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

def get_signature(key='', msg=''):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

def get_headers(api_key='', api_secret_key=''):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {
        'Authorization': 'HMAC-SHA256 ApiKey=' + api_key + ', Date=' + date + ', salt=' + salt + ', signature=' +
                         get_signature(api_secret_key, data),
        'Content-Type': 'application/json; charset=utf-8'
    }

default_agent = {
    'sdkVersion': 'python/4.2.0',
    'osPlatform': platform.platform() + " | " + platform.python_version()
}

def send_one(data):
    data['agent'] = default_agent
    return requests.post(get_url('/messages/v4/send'),
                         headers=get_headers(Config.COOLSMS_API_KEY, Config.COOLSMS_API_SECRET),
                         json=data)

def send_sms(to, text):
    data = {
        'message':{
            'to': to,
            'from': Config.COOLSMS_SENDER_NUMBER,
            'text': text
        },
    }
    # res = send_one(data)
    res = None
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))

    return res