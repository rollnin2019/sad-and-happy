#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/6/29 18:59
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import commands
import logging
import datetime

def exec_shell(cmd):
	logging.warn('===>cmd:{} '.format(cmd))
	#
	print "cmd="+str(cmd)
	status, output = commands.getstatusoutput(cmd)
	print "status=:" + str(status)
	print "status=:" + str(output)

	logging.warn('status:{} output:{}'.format(status, output))
	# if status and -1 == output.find("already exists"):
	# 	logging.error('cmd:{} status:{} output:{}'.format(cmd,status,output))
	return True if 0 == status else False


def delay_date(s = 1, isNeedDate=True):
	now = datetime.datetime.now()
	m = now + datetime.timedelta(seconds=s)

	if isNeedDate:
		f = '%Y-%m-%d'
	else:
		f = '%Y-%m-%d %H:%M:%S'

	return m.strftime(f)


def get_current_date(isNeedDate=True):
	return delay_date(0, isNeedDate)


if __name__ == '__main__':
    print delay_date(s = 1, isNeedDate=False)


