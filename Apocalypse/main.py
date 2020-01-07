#!/usr/bin/env
# coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from pluginManager import PluginManager
from pluginManager import __ALLMODEL__
import time

if __name__ == '__main__':
    # 加载所有插件
    PluginManager.load_all_plugin()
    while True:
        time.sleep(3)
        # 遍历所有接入点下的所有插件
        for single_model in __ALLMODEL__:
            plugins = single_model.get_plugin_object()
            for item in plugins:
                # 调用接入点的公共接口
                item.start()





