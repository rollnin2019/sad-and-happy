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

    # centos7 yum install ipset
    # 创建一个ipset
    def create(self, setname, timeout=0, max=1000000):
        set_cmd = 'ipset create {0} hash:ip timeout {1} maxelem {2} '.format(setname, timeout, str(max))
        # print set_cmd
        return exec_shell(set_cmd)

    def save(self):
        self.exec_shell('ipset save > {0}'.format(self.config))

    def add(self, ip, timeout, type):
        setname = IP_SETS[type]
        code = exec_shell('ipset -exist add {0} {1} timeout {2}'.format(setname, ip, timeout))
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


class pluginIPManger(ModelComponent):
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

        self.IPM = IPSetManger()

    # 实现接入点的接口
    @catch_exception
    @cost
    def start(self):
        print "start PluginIPManger !"
        # ipset list
        # ipset destroy name
        r = self.IPM.create(IP_SETS[0])
        # print "r="+str(r)
        if r:
            self.init_list(self.r3, 0)

        r = self.IPM.create(IP_SETS[1])
        if r:
            self.init_list(self.r4, 1)

        IPTablesManger()
        self.set_ips()

    @catch_exception
    @cost
    def init_list(self, rdc, type):
        # print "ente init_list func"
        logging.warn('init list-{}'.format(str(type)))

        keys = rdc.keys()
        for k in keys:
            code = int(rdc.hget(k, 'status'))  # 0:默认, 10:待拉黑,11:已拉黑,12:待删除黑IP, 20:待加白, 21:已加白,22:待删除白IP

            if code not in [11, 21]:
                #  ls = [11 21]
                continue

            if type == 0:
                count = int(rdc.hget(k, 'count'))
                # t = 0 if count > MAX_BLACK else count * LEVEL
                t = 0 if count > MAX_BLACK else count * LEVEL
                self.IPM.black(k, t)
            else:
                self.IPM.white(k)

    # print 'end'

    def set_ips(self):
        # logging.warn('start set ips {}.'.format(self.local_ip))
        try:
            # print "start set ips"
            logging.warn('start set ips')
            _k1 = self.r1.keys()
            _k2 = self.r2.keys()

            _k = list(k for k in set(_k1).union(set(_k2)) if len(k) >= 7)

            for k in _k:
                _r = self.r1 if k in _k1 else self.r2
                # tmp = _r.hmget(k,'status', 'ip', 'count', 'unblock_at')
                # code = int(_r.hget(k, 'status'))  # 0:默认, 10:待拉黑,11:已拉黑,12:待删除黑IP, 20:待加白, 21:已加白,22:待删除白IP

                # re == new  field for reids-ip-data
                tmp = _r.hmget(k, 'status', 'ip', 'count', 'unblock_at', 're')

                # if re expired,do nothing

                pass

                code = int(tmp[0])

                # add status == 0,11 to avoid bingfa
                if code not in [0, 10, 11, 12, 20, 21,22]:
                    continue

                # print "code not in [10, 12, 20, 22]:"

                # ip = _r.hget(k, 'ip')
                ip = tmp[1]

                # get re
                re = _r.hget(k, 're')
                if not re:
                    print "wrong re"
                    continue

                if not ip:
                    continue

                re = int(re)

                # count = int(_r.hget(k, 'count'))

                count = tmp[2]

                if (10 == code and re == 10) or (11 == code and re == 10):
                    # count = 0
                    if int(count) > MAX_BLACK:

                        t = 0
                        unblock = '9999-99-99 99:99:99'
                    else:
                        t = int(count) * LEVEL
                        unblock = delay_date(t, False)

                    r = self.IPM.black(ip, t)

                    if r:
                        # _r.hset(k, 'status', 11)
                        # _r.hset(k, 'unblock_at', unblock)
                        _v = {'status': 11, 'unblock_at': unblock}
                        _r.hmset(k, _v)
                    else:
                        logging.warn("[FAILED!] add black ip {} ".format(ip))
                elif (20 == code and re == 20) or (21 == code and re == 20):
                    # 加白操作
                    r = self.IPM.white(ip)
                    if r:
                        _v = {'status': 21, 'unblock-at': '_', 'updated_at': delay_date(0, False)}
                        _r.hmset(k, _v)
                    # _r.hset(k, 'status', 21)
                    # _r.hset(k, 'unblock_at', "-")
                    # _r.hset(k, 'updated_at', delay_date(0, False))
                    else:
                        logging.warn("[FAILED!] add white ip {} ".format(ip))


                elif (12 == code and re == 12) or (code == 0 and re == 12):
                    #  unblack ip
                    r = self.IPM.unblack(ip)
                    if r:
                        # _r.hset(k, 'status', 0)
                        # _r.hset(k, 'unblock_at', "-")
                        # _r.hset(k, 'updated_at', delay_date(0, False))
                        _v = {'status': 0, 'unblock-at': '_', 'updated_at': delay_date(0, False), 're': 12}
                        _r.hmset(k, _v)
                    else:
                        logging.warn("[FAILED!] remove black ip {} ".format(ip))
                # elif 22 == code:
                elif (22 == code and re == 22) or (code == 0 and re == 22):
                    # un white
                    r = self.IPM.unwhite(ip)
                    if r:
                        # _r.hset(k, 'status', 0)
                        # _r.hset(k, 'unblock_at', "-")
                        # _r.hset(k, 'updated_at', delay_date(0, False))
                        _v = {'status': 0, 'unblock-at': '_', 'updated_at': delay_date(0, False)}
                        _r.hmset(k, _v)
                    else:
                        logging.warn("[FAILED!] remove white ip {} ".format(ip))
        except Exception, e:
            logging.error(e.message)
