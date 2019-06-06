import jwt
import time
import base64
import json
import tempfile
from uuid import uuid4
from  handler.base import BaseHandler
from sql.sql_method import BlogModel, SystemModel
from util import static_method
from config import JWT_CONFIG
from util.decorator import user_auth
from components.chatroomsdk import ChatRoomSDk

try:
    from dev_config import *
except:
    IMG_URL_BASE = "http://47.93.19.60/static/image/blog/"
    SAVE_FILE_PATH = "/root/kenny/static/image/blog/"


class IndexHandler(BaseHandler):
    """博客列表"""
    @user_auth
    async def get(self):
        user = await self.userauth
        if not user:
            self.redirect(self.get_login_url())
            return
        blog_list = await BlogModel().get_blog_list()
        info = dict(
            blog_list=blog_list
        )
        self.render('home.html', **info)

class BlogDetailHandler(BaseHandler):
    @user_auth
    async def get(self, bid):
        blog_detail = await BlogModel().get_blog_detail(bid)
        blog_prev = await BlogModel().get_blog_prev(blog_detail)
        blog_next = await BlogModel().get_blog_next(blog_detail)


        info = dict(
            blog_detail=blog_detail,
            blog_prev=blog_prev,
            blog_next=blog_next
        )
        self.render('base.html', **info)

class BlogWriteHandler(BaseHandler):
    @user_auth
    async def get(self):
        bid = self.get_argument('bid', '')
        username = await self.session.get('useruuid')
        if not bid:
            info = dict(
                blog_detail={},
                username=username
            )
        else:
            blog_detail = await BlogModel().get_blog_detail(bid)
            info = dict(
                blog_detail=blog_detail,
                username=username
            )
        self.render('index.html', **info)

    @user_auth
    async def post(self):
        content = self.get_argument('c', '')
        title = self.get_argument('t', '')
        bid = self.get_argument('bid', '')
        if not title or not content:
            self.finish(static_method.return_code(500, "请填写完整信息"))
            return
        if bid:
            res = await BlogModel().modify_blog(bid, title, content)
        else:
            res = await BlogModel().write_blog(title, content)
        info = static_method.return_code(100, res)
        self.finish(info)

class BlogModifyHandler(BaseHandler):
    async def get(self, bid):
        blog_detail = await BlogModel().get_blog_detail(bid)
        username = await self.session.get('useruuid')
        info = dict(
            blog_detail=blog_detail,
            username=username
        )
        self.render('index.html', **info)

class LoginHandler(BaseHandler):
    async def get(self):
        self.render('login.html')

    async def post(self):
        username = self.get_argument('u', '')
        password = self.get_argument('p', '')
        isrember = self.get_argument('r', '')
        if not username or not password:
            self.finish(static_method.return_code(500, '请填写账号密码'))
            return
        if username == 'liudong' and password == '123kkk':
            if isrember:
                await self.session.set("useruuid", username, exp=86400*30)
            else:
                await self.session.set("useruuid", username)
            token, useruuid = await ChatRoomSDk().get_user_info(username)
            # print (token)
            # print (useruuid)
            # await self.session.set("uuid", useruuid)
            # await self.session.set("token", token)
            self.finish(static_method.return_code(100, 'success'))
            return
        self.finish(static_method.return_code(500, '账号密码错误'))
        return

class LogoutHandler(BaseHandler):
    async def get(self):
        await self.session.cleanup()
        self.redirect(self.get_login_url())

class JwtAuthHandler(BaseHandler):
    async def get(self):
        payload = {
            "iss": JWT_CONFIG['iss'],  # 该JWT的签发者，是否使用是可选的
             "iat": int(time.time()),  # 在什么时候签发的（UNIX时间），是否使用是可选的
             "exp": int(time.time()) + 86400 * 7,  # 什么时候过期，这里也是一个UNIX的时间戳，是否使用也是可以选择的;
             "aud": JWT_CONFIG['aud'],  # 接收JWT的的一方，是否使用也是可选的
             "username": 'kenny'
        }
        jwt_token = jwt.encode(payload, JWT_CONFIG['secret'], algorithm=JWT_CONFIG['alg'])
        self.finish(jwt_token)

    async def post(self):
        token = self.get_argument('token', '')
        payload = jwt.decode(token, JWT_CONFIG['secret'], audience=JWT_CONFIG['aud'], algorithms=JWT_CONFIG['alg'])
        print (payload)
        self.finish(payload)

class UploadFileHandler(BaseHandler):
    # executor = ThreadPoolExecutor(64)
    async def post(self):
        response = await self._upload()
        self.write(response)
        self.finish()

    # @run_on_executor
    async def _upload(self):
        baseimg = self.get_argument('img','')
        basefile = []
        if baseimg:
            baseimg = baseimg.split(',')[1]
            imgData = base64.b64decode(baseimg)
            basefile.append({"content_type":"image/png","filename":"base64.png","body":imgData})

        file_metas = basefile if baseimg else self.request.files['file'] # 提取表单中‘name’为‘fileToUpload’的文件元数据


        for f in file_metas:
            filetype = f['content_type']

            # 获取后缀名
            rawname = f['filename']
            if rawname=='blob':
                _suffix = 'png'
            else:
                try:
                    _suffix = rawname.split('.').pop()
                except:
                    _suffix = None
            suffix = _suffix.lower() if _suffix else None
            if suffix not in ('png','jpg','jpeg','gif','doc','docx','xls','xlsx','pdf','ppt','pptx','txt'):
                self.finish(static_method.return_code(500, "type error"))
                return
            tf = tempfile.NamedTemporaryFile()
            tf.write(f['body'])
            tf.seek(0)
            orgfileuuid = static_method.get_file_mD5(tf)

            # 从数据库查询，是否已有这个文件
            uuid = str(uuid4())
            filename = uuid+ '.'+ suffix
            fileinfo = await SystemModel().get_file(orgfileuuid)
            # imgurl = "http://192.168.22.100:8000/static/image/blog/"+filename
            imgurl = IMG_URL_BASE+filename
            if fileinfo:
                # 已经存在这个文件了
                tf.close()
                info = {'status':1, 'url':fileinfo['file_path']}
                return json.dumps(info)
            files = open(SAVE_FILE_PATH+filename, 'wb')
            # files = open('/home/toby/work/kenny/static/image/blog/'+filename, 'wb')
            files.write(f['body'])
            files.close()
            await SystemModel().save_file(orgfileuuid, imgurl)
            info = {'status':1, 'url':imgurl}
            return json.dumps(info)

class ApiGetBlogHandler(BaseHandler):
    """
    请求的参数都是放在body中，主要是看body中是以什么形式（content-type）提交的
    1.content-type=form-data表单形式提交：使用self.get_argument可以取出参数
    2.content-type=x-www-form-urlencoded形式提交：使用self.get_argument可以取出参数
    3.content-type=text/plain在postman中写的是RAW:参数在self.request.body中，需单独封装方法取出参数
    """
    async def get(self):
        """取出一个资源"""
        blog_list = await BlogModel().get_blog_list()
        info = dict(
            blog_list=blog_list
        )
        self.set_status(200, 'OK')
        self.finish(static_method.return_code(100, info))

    async def post(self):
        """新建一个资源"""
        print (self.request.headers)
        bid = self.get_argument('bid')
        print (bid)

    async def put(self):
        """在服务器更新资源（客户端提供改变后的完整资源）"""
        pass
    async def patch(self):
        """在服务器更新资源（客户端提供改变的属性）"""
        pass

    async def delete(self):
        """从服务器删除资源。"""
        pass

class ChatHandler(BaseHandler):
    async def get(self):
        endPoint = ChatRoomSDk().endPoint
        port = ChatRoomSDk().port
        username = await self.session.get('uuid')
        self.render("chatroom.html", endPoint=endPoint.replace("http://", ""), port=port, username=username)

class RoomListHandler(BaseHandler):
    async def get(self):
        room_info = await ChatRoomSDk().get_room_list()
        self.render()

    async def post(self):
        roomid = self.get_argument("roomid", "")
        token = await self.session.get('token')
        res = await ChatRoomSDk().join_chat_room(roomid, token)
        if res == 100:
            self.finish(static_method.return_code(100, '加入成功'))
        elif res == 200:
            self.finish(static_method.return_code(100, '你已经在房间了'))
        else:
            self.finish(static_method.return_code(500, '系统错误'))
        return