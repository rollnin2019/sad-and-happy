#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/6/27 16:09
Created by Admin
"""

import sys

import functools

reload(sys)
sys.setdefaultencoding('utf-8')
import logging
from time import time


def catch_exception(origin_func):
	@functools.wraps(origin_func)
	def wrapper(self, *args, **kwargs):

		try:
			return origin_func(self, *args, **kwargs)
		except Exception as e:
			msg = "args:{}, msg:{}".format(e.args, e.message)
			_log_msg = "[{}.{}] msg::{} ".format(self.__class__.__name__, origin_func.__name__, msg)
			logging.error(_log_msg)
			return False

	return wrapper


def catch_exception_common(origin_func):
	@functools.wraps(origin_func)
	def wrapper(*args, **kwargs):

		try:
			return origin_func(*args, **kwargs)
		except Exception as e:
			msg = "args:{}, msg:{}".format(e.args, e.message)
			_log_msg = "[func-{}] msg::{} ".format(origin_func.__name__, msg)
			logging.error(_log_msg)

			return False

	return wrapper



def cost(func):
	def wrapper(self, *args, **kwargs):
		b = time()
		r = func(self, *args, **kwargs)
		e = time()
		logging.warn("cost {}".format(str(e-b)))
		return r
	return wrapper


