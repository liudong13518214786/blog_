from handler.base import BaseModel
from util.decorator import memcache_for_method
from util import static_method
class TestModel(BaseModel):
    async def insertone(self):
        sqlstr = """INSERT INTO test (name, money) values ('liudong1', '101');"""
        rv = await self.db.exec_safe(sqlstr)
        return rv
    # @memcache_for_method(10)
    async def getone(self):
        sqlstr = """SELECT * FROM test;"""

        rv = await self.db.findone_safe(sqlstr)
        return rv

    async def getmany(self):
        sqlstr = """SELECT * FROM test;"""
        rv = await self.db.query_safe(sqlstr)
        return rv

    async def update_one(self):
        sqlstr = """UPDATE test SET money='你好' where name='liudong1';"""
        rv = await self.db.exec_safe(sqlstr)
        return rv

    async def trans(self):
        sqlstr = """INSERT INTO test (name, money) values ('liudong7', '888');"""
        self.db.transaction_exec_safe(sqlstr)
        sqlstr = """UPDATE test SET money='你好A' where name='liudong7';"""
        self.db.transaction_exec_safe(sqlstr)
        rv = await self.db.transaction_commit_safe()
        return rv

class BlogModel(BaseModel):
    async def get_blog_list(self):
        sqlstr = """SELECT * FROM blog WHERE status='normal' ORDER BY build_time DESC ;"""
        result = await self.db.query_safe(sqlstr)
        return result

    async def get_blog_detail(self, bid):
        sqlstr = """SELECT * FROM blog WHERE uuid=%s AND status='normal';"""
        result = await self.db.findone_safe(sqlstr, bid)
        return result

    async def get_blog_prev(self, info):
        sqlstr = """SELECT * FROM blog WHERE build_time>%s AND status='normal' ORDER BY build_time ASC LIMIT 1;"""
        result = await self.db.findone_safe(sqlstr, info['build_time'])
        return result

    async def get_blog_next(self, info):
        sqlstr = """SELECT * FROM blog WHERE build_time<%s AND status='normal' ORDER BY build_time DESC LIMIT 1;"""
        result = await self.db.findone_safe(sqlstr, info['build_time'])
        return result

    async def write_blog(self, title, info):
        uuid = static_method.create_random_string(16)
        build_time = static_method.get_datetime()

        sqlstr = """INSERT INTO blog(uuid, title, build_time, status, info) VALUES (%s,%s,%s,%s,%s);"""
        result = await self.db.exec_safe(sqlstr, uuid, title, build_time, 'normal', info)
        return result

    async def modify_blog(self, bid, title, info):
        sqlstr = """UPDATE blog SET title=%s, info=%s WHERE uuid=%s AND status='normal';"""
        result = await self.db.exec_safe(sqlstr, title, info, bid)
        return result

class SystemModel(BaseModel):
    async def get_file(self, file_uuid):
        sqlstr = """SELECT * FROM file WHERE uuid=%s;"""
        result = await self.db.findone_safe(sqlstr, file_uuid)
        return result


    async def save_file(self, uuid, file_path):
        sqlstr = """INSERT INTO file(uuid, file_path, build_time, status) VALUES (%s,%s,%s,%s);"""
        result = await self.db.exec_safe(sqlstr, uuid, file_path, static_method.get_datetime(), 'normal')
        return result