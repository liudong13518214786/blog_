import asyncio
from aiocache import caches
from config import MEMCACHE_CONFIG
caches.set_config({
    'default': {
        'cache': "aiocache.MemcachedCache",
        'endpoint': MEMCACHE_CONFIG['host'],
        'port': MEMCACHE_CONFIG['port'],
        'serializer': {
            'class': "aiocache.serializers.StringSerializer"
        }
    }
})
memcache = caches.get('default')

async def cache_get(key):
    value = await memcache.get(key)
    return value

async def cache_set(key, value,exp=86400):
    result = await memcache.set(key, value, ttl=exp)
    return result

async def cache_del(key):
    result = await memcache.delete(key)
    return result

