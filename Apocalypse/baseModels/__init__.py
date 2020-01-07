#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/7/2 10:33
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__engine = create_engine("mysql+pymysql://lee:{}@103.198.75.117:7801/gongdan".format('lee@tulong'))
SESSION = scoped_session(sessionmaker(bind=__engine))
BASE = declarative_base()
