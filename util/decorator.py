import functools
import urllib.parse as urlparse
from urllib.parse import urlencode
from tornado.web import HTTPError
import jwt
from util import static_method
from components import cache
from components.database import async_mysql_client
from config import JWT_CONFIG

def memcache_for_method(exp=0):
    """给sql查询方法加缓存， 缓存时间默认0, 0是永久缓存"""
    def decorator(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            memecache_key = method.__name__
            memecache_key += ''.join([i for i in args])
            memecache_key += ''.join([str(j) + str(kwargs[j]) for j in kwargs])
            md5str = static_method.get_md5(memecache_key)
            result = await cache.cache_get(md5str)
            if result is not None:
                return result
            else:
                result = await method(self, *args, **kwargs)
                if exp == 0:
                    sqlstr = """SELECT uuid FROM cache_control WHERE uuid=%s;"""
                    res = await async_mysql_client.query_safe(sqlstr, memecache_key)
                    if not res:
                        uuid = static_method.create_random_string(32)
                        sqlstr = """INSERT INTO cache_control(uuid, build_time, status) VALUES(%s, %s, %s);"""
                        await async_mysql_client.exec_safe(sqlstr, uuid, static_method.get_datetime(), 'normal')

                await cache.cache_set(md5str, result, exp=exp)
                return result
        return wrapper
    return decorator

def user_auth(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        useruuid = await self.session.get("useruuid")
        if not useruuid:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)
        return await method(self, *args, **kwargs)
    return wrapper

def jwtauth(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        auth = self.request.headers.get("Authorization")  # 先定义JWT-TOKEN放在heads中
        if not auth:
            self.set_status(404)
            self.finish("Missing Authorization")
        _auth = auth.split()
        if _auth[0].lower != "kenny" or len(_auth) != 2:
            self.set_status(404)
            self.finish("Invalid header Authorization")
        token = _auth[1]
        try:
            jwt.decode(
                token,
                JWT_CONFIG['secret'],
                audience=JWT_CONFIG['aud'],
                algorithms=[JWT_CONFIG['alg']]
            )
            return func(*args, **kwargs)
        except Exception as err:
            self.set_status(401)
            self.finish(err)
    return wrapper
