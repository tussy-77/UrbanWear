from flask_caching import Cache

# SimpleCache: in-process memory, resets on restart, single-worker only.
# For multi-worker production: CACHE_TYPE=RedisCache + CACHE_REDIS_URL in .env
cache = Cache()
