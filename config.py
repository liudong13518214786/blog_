import os
try:
        from dev_config import *
except:
        DATABASE_PASSWORD = '200826'
        DATABASE_NAME = 'blog'
# 数据库配置
MYSQL_DATABASE_CONFIG = dict(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        passwd=os.getenv("MYSQL_PASSWD", DATABASE_PASSWORD),
        db=os.getenv("MYSQL_DB", DATABASE_NAME),
        charset=os.getenv("MYSQL_CHARSET", "utf8"),
        # sql_mode="REAL_AS_FLOAT",
        # init_command="SET max_join_size=DEFAULT"
    )

PG_DATABASE_CONFIG = dict()


# memcache配置``
MEMCACHE_CONFIG = dict(
        host="127.0.0.1",
        port=11211
)

JWT_CONFIG = dict(
        secret="Y6MUyiZjZv69bIh6K1ZD5jTRcq3yP8IC",
        iss="blog.xxx.com",
        aud="www.xxx.com",
        alg="HS256"
)