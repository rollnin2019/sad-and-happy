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
import time
from pluginManager import ModelComponent
from plugins.ipManger.config import *
from common.utils import *
from common.decorator import catch_exception, cost
from redis import *


class IPTablesManger(object):
	def __init__(self):
		# print 'adminIPManager init'
		if not self.is_black_rule_exist():
			self.add_black_rule()

		if not self.is_white_rule_exist():
			self.add_white_rule()

	def is_black_rule_exist(self):
		_rule = RULE.format(CHK, IP_SETS[0], DROP)
		return exec_shell(_rule)

	def is_white_rule_exist(self):
		_rule = RULE.format(CHK, IP_SETS[1], ACCEPT)
		return exec_shell(_rule)

	def add_black_rule(self):
		_rule = RULE.format(INS, IP_SETS[0], DROP)
		return exec_shell(_rule)

	def add_white_rule(self):
		_rule = RULE.format(INS, IP_SETS[1], ACCEPT)
		return exec_shell(_rule)

	def del_black_rule(self):
		_rule = RULE.format(DEL, IP_SETS[0], DROP)
		return exec_shell(_rule)

	def del_white_rule(self):
		_rule = RULE.format(DEL, IP_SETS[1], DROP)
		return exec_shell(_rule)


class IPSetManger(object):
	def __init__(self):
		self.config = "/ipsets.txt"

	def create(self, setname, timeout=0, max=1000000):
		set_cmd = 'ipset create {0} hash:ip timeout {1} maxelem {2} '.format(setname, timeout, str(max))
		return exec_shell(set_cmd)

	def save(self):
		self.exec_shell('ipset save > {0}'.format(self.config))

	def add(self, ip, timeout, type):
		setname = IP_SETS[type]
		# print '{0} {1} {2}'.format(setname, ip, timeout)
		code = exec_shell('ipset -exist add {0} {1} timeout {2}'.format(setname, ip, timeout))
		# print code
		return code

	def delete(self, ip, type):
		setname = IP_SETS[type]
		code = exec_shell('ipset del {0} {1}'.format(setname, ip))
		return code

	def black(self, ip, timeout=0, type=0):
		return self.add(ip, timeout, type)

	def white(self, ip, timeout=0, type=1):
		return self.add(ip, timeout, type)

	def unblack(self, ip, type=0):
		return self.delete(ip, type)

	def unwhite(self, ip, type=1):
		return self.delete(ip, type)


class pluginAdminIPManger(ModelComponent):

	def __init__(self):
		p1 = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB_SELF, decode_responses=True)  # 手动库

		self.r1 = Redis(connection_pool=p1)
		self.IPM = IPSetManger()

	# 实现接入点的接口
	@catch_exception
	@cost
	def start(self):
		print "***************************"
		print "start AdminPluginIPManger !"

		r1 = self.IPM.create(IP_SETS[0])
		r2 = self.IPM.create(IP_SETS[1])
		if r1 and r2:
			self.init_list(self.r1)

		IPTablesManger()
		self.set_ips()

	def set_ips(self):
		try:
			logging.warn('adminIPManager start set ips')
			_k1 = self.r1.keys()
			_k = list(k for k in set(_k1) if len(k) >= 7)
			# print "Admin _k="
			# print _k

			for k in _k:

				_r = self.r1
				tmp = _r.hmget(k,'status', 'ip', 'count', 'unblock_at')

				code = int(tmp[0])
				# print "code"
				# print code
				if code not in [10, 12, 20, 22]:
					continue

				ip = tmp[1]
				if not ip:
					continue

				# count = int(_r.hget(k, 'count'))
				count = tmp[2]

				if 10 == code:
					if count > MAX_BLACK:
						t = 0
						unblock = '9999-99-99 99:99:99'
					else:
						t = count * LEVEL
						unblock = delay_date(t, False)

					ip = str(ip)
					# 先删白名单，再加黑
					self.IPM.unwhite(ip)
					r = self.IPM.black(ip, t)
					print r
					if r:
						_v = {'status': 11, 'unblock_at': unblock}
						_r.hmset(k, _v)
					else:
						logging.warn("[FAILED!] add black ip {} ".format(ip))

				elif 20 == code:
					# 加白操作
					#先删黑名单，再加白
					self.IPM.unblack(ip)
					r = self.IPM.white(ip)
					print r
					if r:

						_v = {'status': 21, 'unblock-at': '_', 'updated_at': delay_date(0, False)}
						_r.hmset(k, _v)
					else:
						logging.warn("[FAILED!] add white ip {} ".format(ip))

				elif 12 == code or 22 == code:
					r1 = self.IPM.unblack(ip)
					r2 = self.IPM.unwhite(ip)

					_v = {'status': 0, 'unblock-at': '_', 'updated_at': delay_date(0, False)}
					_r.hmset(k, _v)

					# if not r1 and not r2:
					# 	logging.warn("[FAILED!] remove ip {} ".format(ip))
					# else:
					# 	_v = {'status': 0, 'unblock-at': '_', 'updated_at': delay_date(0, False)}
					# 	_r.hmset(k, _v)

				# elif 22 == code:
				#
				# 	r = self.IPM.unwhite(ip)
				# 	r = self.IPM.unblack(ip)
				#
				# 	if r:
				#
				# 		_v = {'status': 0, 'unblock-at': '_', 'updated_at': delay_date(0, False)}
				# 		_r.hmset(k, _v)
				# 	else:
				# 		logging.warn("[FAILED!] remove white ip {} ".format(ip))
		except Exception, e:
			logging.error(e.message)

	@catch_exception
	@cost
	def init_list(self, rdc):
		# logging.warn('init list-{}'.format(str(type)))

		ls = [11, 21]
		keys = rdc.keys()
		for k in keys:
			code = int(rdc.hget(k, 'status'))  # 0:默认, 10:待拉黑,11:已拉黑,12:待删除黑IP, 20:待加白, 21:已加白,22:待删除白IP
			if code not in ls:
				# ls  = [11 ,21]
				continue

			if code == 11:
				count = int(rdc.hget(k, 'count'))
				t = 0 if count > MAX_BLACK else count * LEVEL
				# self.IPM.black(k, t)
				self.IPM.black(rdc.hget(k, 'ip'), t)
			elif code == 21:
				# self.IPM.white(k)
				self.IPM.white(rdc.hget(k, 'ip'))


