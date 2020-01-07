#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/7/10 15:12
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import threading
import time


class Singleton(object):
	_Singleton_lock = threading.Lock()

	def __init__(self):
		time.sleep(1)

	@staticmethod
	def instance():
		if not hasattr(Singleton, "_inst"):
			with Singleton._Singleton_lock:
				if not hasattr(Singleton, "_inst"):
					Singleton._inst = Singleton()

		return Singleton._inst

	@staticmethod
	def instance2():
		if not hasattr(Singleton, "_inst"):
			Singleton._inst = Singleton()

		return Singleton._inst


class Singleton2(object):
	_Singleton2_lock = threading.Lock()

	def __init__(self):
		print "__init__"

	def __new__(cls, *args, **kwargs):
		if not hasattr(Singleton2, "_inst"):
			with Singleton2._Singleton2_lock:
				if not hasattr(Singleton2, "_inst"):
					Singleton2._inst = object.__new__(cls)

		return Singleton2._inst


class Singleton3(type):
	_instance_lock = threading.Lock()

	def __call__(self, *args, **kwargs):
		if not hasattr(self, "_inst"):
			with Singleton3._instance_lock:
				if not hasattr(self, "_inst"):
					self._inst = super(Singleton3, self).__call__(*args, **kwargs)
		return self._inst


class Foo(object):

	__metaclass__ = Singleton3


import requests


def get_test():
	_url = 'http://144.0.1.22/api/v1.0/get_local_addr?GID=00000010&TOKEN=70C78BCC6F47190111C875AC503857120f&TIMESTAMP=160d4c94b73'

	for i in xrange(100):
		try:
			r = requests.get(_url)
			print "{}--{}".format(i, r.status_code)
		except Exception, e:
			print e.message


class MyThread(threading.Thread):
	def __init__(self, arg):
		super(MyThread, self).__init__()
		self.arg = arg

	def run(self):
		time.sleep(1)
		obj = Foo()
		print "{}".format(obj)

	# get_test()


for i in xrange(10):
	t = MyThread(i)
	t.start()
