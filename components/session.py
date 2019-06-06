import json
from util import static_method
from components import cache

class SessionMoel(object):
    def __init__(self, handler):
        self.SESSION_NAME = 'BLOG'
        self.handler = handler
        super(SessionMoel, self).__init__()

    def create_session_id(self):
        uuid = static_method.create_random_string(16)
        self.handler.set_secure_cookie(self.SESSION_NAME, uuid, expires_days=None)
        return uuid

    def get_session_id(self):
        session_id = self.handler.get_secure_cookie(self.SESSION_NAME)
        if not session_id:
            session_id = self.create_session_id()
        return str(session_id)

    async def set(self, name, value, exp=86400):
        session_id = self.get_session_id()
        cache_key = "{0}_{1}".format(session_id, name)
        result = await cache.cache_set(cache_key, value, exp=exp)
        if result:
            await self.save_keyarr(session_id, name)
        return result

    async def get(self, key):
        session_id = self.get_session_id()
        cache_key = '{0}_{1}'.format(session_id, key)
        value = await cache.cache_get(cache_key)
        return value

    async def save_keyarr(self, session_id, key):
        """
        把session的键值记录在字典中
        :param session_id:
        :param key:
        :return:
        """
        save_key = session_id+'_blogsession'
        keyarr = await cache.cache_get(save_key)
        print (keyarr)
        if keyarr:
            keyarr[key] = '1'
        else:
            keyarr = {key:'1'}
        await cache.cache_set(save_key, json.dumps(keyarr))

    async def clear_key(self, session_id):
        save_key = session_id+'_blogsession'
        _keyarr = await cache.cache_get(save_key)
        if _keyarr:
            keyarr = json.loads(_keyarr)
            if keyarr:
                for (k,v) in keyarr.items():
                    cache_key = '{0}_{1}'.format(session_id, k)
                    await cache.cache_del(cache_key)
            await cache.cache_del(save_key)

    async def cleanup(self):
        session_id = self.get_session_id()
        await self.clear_key(session_id)

class XsessionMiniModel(object):
    @property
    def session(self):
        """
        Returns a SessionManager instance
        """
        return create_mixin(self, 'user_xminasession_manager', SessionMoel)
    
def create_mixin(context, manager_property, manager_class):
    if not hasattr(context, manager_property):
        setattr(context, manager_property, manager_class(context))
    return getattr(context, manager_property)