#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME :blog_
# CREATETIME   :2019-06-06
# AUTHOR       :liudong
import tornado.httpclient
import tornado.gen
import json
class ChatRoomSDk(object):
    _instance = {}

    def __init__(self):
        self.endPoint = "http://172.16.11.173"
        self.port = 8081

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(ChatRoomSDk, cls).__new__(cls, *args, **kwargs)
        return cls._instance[cls]

    async def get_user_info(self, username):
        """
        获取聊天用户信息，如果有就返回，没有就创建
        :param username:
        :return:
        """
        uri = "/v1/use?u=" +username
        req = tornado.httpclient.HTTPRequest(url=f'{self.endPoint}:{self.port}/{uri}', method='GET')
        client = tornado.httpclient.AsyncHTTPClient()
        resp = await tornado.gen.Task(client.fetch, req)
        body = json.loads(resp.body)
        if body and body.get("code") == 100:
            token = body.get("message")
            useruuid = body.get("useruuid")
        else:
            token = ""
            useruuid = ""
        return token, useruuid

    async def create_chat_room(self, token):
        uri = "/v1/join"
        headers = {
            "token": token
        }
        req = tornado.httpclient.HTTPRequest(url=f'{self.endPoint}:{self.port}/{uri}', method='GET', headers=headers)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = await tornado.gen.Task(client.fetch, req)
        body = json.loads(resp.body)
        if body and body.get("code") == 100:
            roomid = body.get("message")
        else:
            roomid = ""
        return roomid

    async def join_chat_room(self, roomid, token):
        uri = "/v1/join?roomid="+roomid
        headers = {
            "token": token
        }
        req = tornado.httpclient.HTTPRequest(url=f'{self.endPoint}:{self.port}/{uri}', method='POST', headers=headers)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = await tornado.gen.Task(client.fetch, req)
        body = json.loads(resp.body)
        if body:
            code = body.get("code")
        else:
            code = ""
        return code

    async def get_room_list(self):
        uri = "/v1/room"
        req = tornado.httpclient.HTTPRequest(url=f'{self.endPoint}:{self.port}/{uri}', method='GET')
        client = tornado.httpclient.AsyncHTTPClient()
        resp = await tornado.gen.Task(client.fetch, req)
        body = json.loads(resp.body)
        if body and body.get("code") == 100:
            roomlist = body.get("message")
        else:
            roomlist = []
        return roomlist