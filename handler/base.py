import json
import tornado.web
from components.database import async_mysql_client
from components.session import XsessionMiniModel

class BaseHandler(tornado.web.RequestHandler, XsessionMiniModel):
    @property  # @property可以把一个实例方法变成其同名属性，以支持.号访问，它亦可标记设置限制，加以规范
    def db(self):
        return self.application.db
    @property
    async def userauth(self):
        res = await self.session.get('useruuid')
        return res

    def get_parms(self, name, default='', strip=True):
        request_body = self.request.body
        body = json.loads(request_body)
        return body[name]
class BaseModel(object):
    def __init__(self):
        self.db = async_mysql_client
