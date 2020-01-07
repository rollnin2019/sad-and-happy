#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/7/2 10:45
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

'''
	#基础变量
'''

LOCAL_IP = ["103.198.74.134"]

IP_SHELL = 'ifconfig | grep inet | grep -v inet6 | grep -v 127| grep -v 172| sed -e "s/^[ \s]\{1,\}//g" | sed -e "s/[ \s]\{1,\}$//g" |cut -d ' ' -f 2'

IPTABLES = '/usr/sbin/iptables'
ACCEPT = 'ACCEPT'
DROP = 'DROP'

ADD = '-A'
DEL = '-D'
INS = '-I'
CHK = '-C'
'''
	#IPTABLES 防护规则配置
'''

IP_RULE = IPTABLES + ' {} INPUT -s {} -j {}'

'''
REDIS
'''
# REDIS_HOST = '103.198.73.80'
REDIS_HOST = '192.168.20.80'
REDIS_PORT = 6379
REDIS_PWD = 'redis@tulong'
REDIS_DB_AUTO = 10
REDIS_DB_SELF = 13
REDIS_DB_RESULT_B = 11
REDIS_DB_RESULT_W = 12

'''
IPSET
'''
RULE = 'iptables {} INPUT -m set --match-set {} src -j {}'
IP_SETS = ['emod-black-list-admin', 'emod-white-list-admin']

LEVEL = 60*60
DT_STU = {0:[11],1:[21]}
MAX_BLACK = 200