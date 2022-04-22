import redis

from config.db import REDIS_HOST, REDIS_PORT

ref_tok = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
