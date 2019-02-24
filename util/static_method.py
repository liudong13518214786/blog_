# coding:utf-8
import functools
import json
import time
import string
import hashlib
import random
from datetime import datetime,date


random.seed((time.time() + 987.763 * 3.29))


class ComplexEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)

def json_dumps(data_dict):
    try:
        jsonstr = json.dumps(data_dict, cls=ComplexEncoder)
    except Exception as e:
        jsonstr = '{}'
    return jsonstr

def return_code(error_code, msg=None):
    ejson = {'code': error_code}
    if error_code != 100:
        print('#### ERROR code:%s,msg:%s ####' % (error_code,msg))
    if None != msg:
        ejson['msg'] = msg
    # jsonstr = json.dumps(ejson)
    jsonstr = json_dumps(ejson)
    return jsonstr

def get_md5(strs):
    m = hashlib.md5()
    m.update(strs.encode('utf8'))
    return m.hexdigest()

def get_datetime(timestamp=None):
    if timestamp is None:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))

def create_random_string(length=8):
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return ran_str


def get_file_mD5(fdfile):
    md5obj = hashlib.md5()
    md5obj.update(fdfile.read())
    hash = md5obj.hexdigest().upper()
    fdfile.seek(0)
    return hash




