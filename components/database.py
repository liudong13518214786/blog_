# coding:utf-8
import os
import traceback
import logging
from tornado.log import app_log
from tormysql import ConnectionPool, DictCursor
from config import MYSQL_DATABASE_CONFIG
class AsyncMysqlClient(object):
    def __init__(self):
        self.db = ConnectionPool(max_connections=int(os.getenv("MYSQL_POOL", 10)),
                                 idle_seconds=0,  # conntion idle timeout time, 0 is not timeout
                                 # cursorclass=DictCursor,
                                 **MYSQL_DATABASE_CONFIG)
        logging.info("init database success")
        self.adb_trans_sql = []

    def __print_sql(self, sqlstr, parm):
        """打印完整的sql语句，方便调试"""
        _parm = []
        if parm:
            for p in parm:
                _parm.append("'%s'" % p)
            outstr = sqlstr % tuple(_parm)
        else:
            outstr = sqlstr
        logging.info(outstr)
        app_log.debug(outstr)

    async def query_safe(self, sqlstr, *parm):
        result = []
        self.__print_sql(sqlstr, parm)
        with (await self.db.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    await cursor.execute(sqlstr, parm)
                    fetch = cursor.fetchall()
                    if fetch:
                        result = fetch
            except Exception as err:
                errormsg = '[sql_error]' + repr(err)
                app_log.error(errormsg)
                app_log.error(traceback.print_exc())
            else:
                await conn.commit()
        return result

    async def findone_safe(self, sqlstr, *parm):
        result = []
        self.__print_sql(sqlstr, parm)
        with (await self.db.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    await cursor.execute(sqlstr, parm)
                    fetch = cursor.fetchone()
                    if fetch:
                        result = fetch
            except Exception as err:
                errormsg = '[sql_error]' + repr(err)
                app_log.error(errormsg)
                app_log.error(traceback.print_exc())
            else:
                await conn.commit()
        return result

    async def exec_safe(self, sqlstr, *parm):
        result = True
        self.__print_sql(sqlstr, parm)
        with (await self.db.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    await cursor.execute(sqlstr, parm)
            except Exception as err:
                errormsg = '[sql_error]' + repr(err)
                app_log.error(errormsg)
                app_log.error(traceback.print_exc())
                await conn.rollback()
                result = False
            else:
                await conn.commit()
        return result

    def transaction_exec_safe(self, sqlstr, *parm):
        if not self.adb_trans_sql:
            self.adb_trans_sql = []
        sqlstr_task = [sqlstr, parm]
        self.adb_trans_sql.append(sqlstr_task)

    async def transaction_commit_safe(self):
        result = True
        with (await self.db.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    for trans in self.adb_trans_sql:
                        await cursor.execute(trans[0], trans[1])
            except Exception as err:
                errormsg = '[sql_error]' + repr(err)
                app_log.error(errormsg)
                app_log.error(traceback.print_exc())
                await conn.rollback()
                result = False
            else:
                await conn.commit()
        return result

async_mysql_client = AsyncMysqlClient()