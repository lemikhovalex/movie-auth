import redis

from config.db import REDIS_HOST, REDIS_PORT

user_ids = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=3)
user_agents = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=4)
