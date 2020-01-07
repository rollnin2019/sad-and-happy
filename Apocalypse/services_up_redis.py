#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/10/16 16:59
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from services.serv_update import Serv
from time import sleep
if __name__ == '__main__':

	while True:
		s = Serv()
		s.update_redis()
		sleep(0.1)

