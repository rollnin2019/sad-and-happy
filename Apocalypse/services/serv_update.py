#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/7/18 11:11
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# !/usr/bin/env
# coding:utf-8
"""
Created on 2018/7/2 10:39
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from config import *
from common.utils import *
from common.decorator import catch_exception, cost
from redis import *



class Serv():

	def __init__(self):

		p1 = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB_TMP,
		                    decode_responses=True)  # 手动库
		p2 = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB_AUTO,
		                    decode_responses=True)
		p3 = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB_RESULT_B,
		                    decode_responses=True)
		p4 = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB_RESULT_W,
		                    decode_responses=True)
		self.r1 = Redis(connection_pool=p1)
		self.r2 = Redis(connection_pool=p2)
		self.r3 = Redis(connection_pool=p3)
		self.r4 = Redis(connection_pool=p4)

	@cost
	def update_redis(self):
		# logging.warn('start update_redis')

		_k1 = self.r1.keys()
		_k2 = self.r2.keys()
		_k = list(k for k in set(_k1).union(set(_k2)) if len(k) >= 7)

		for k in _k:
			_r = self.r1 if k in _k1 else self.r2
			code = int(_r.hget(k, 'status'))  # 0:默认, 10:待拉黑,11:已拉黑,12:待删除黑IP, 20:待加白, 21:已加白,22:待删除白IP

			if code not in [0, 11, 21]:
				continue

			# logging.warn("code-->{}".format(code))
			tmp = _r.hgetall(k)

			if 'status' in tmp and tmp['status'] == '21':
				self.r4.hmset(k, tmp)
			else:
				self.r3.hmset(k,tmp)

			if 'status' in tmp and tmp['status'] == '0':
				self.r4.delete(k)

			_r.delete(k)


if __name__ == '__main__':
	s = Serv()
	s.update_redis()
