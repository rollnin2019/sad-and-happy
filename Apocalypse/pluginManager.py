#!/usr/bin/env
# coding:utf-8
"""
Created on 2018/6/29 18:23
Created by Admin
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import os
import sys
from imp import find_module
from imp import load_module
import logging


class PluginManager(type):
	# 静态变量配置插件路径
	__plugin_path = 'plugins'

	# 调用时将插件注册
	def __init__(self, name, bases, dict):
		if not hasattr(self, 'all_plugins'):
			self.__all_plugins = {}
		else:
			self.register_all_plugin(self)

	# 设置插件路径
	@staticmethod
	def set_plugin_Path(path):
		if os.path.isdir(path):
			PluginManager.__plugin_path = path
		else:
			print '%s is not a valid path' % path

	# 递归检测插件路径下的所有插件，并将它们存到内存中
	@staticmethod
	def load_all_plugin():
		plugin_path = PluginManager.__plugin_path
		if not os.path.isdir(plugin_path):
			raise EnvironmentError, '%s is not a directory' % plugin_path

		items = os.listdir(plugin_path)
		for item in items:
			if os.path.isdir(os.path.join(plugin_path, item)):
				PluginManager.__plugin_path = os.path.join(plugin_path, item)
				PluginManager.load_all_plugin()
			else:
				if item.startswith('plugin') and item.endswith('.py') and item != '__init__.py':
					module_name = item[:-3]
					if module_name not in sys.modules:
						file_handle, file_path, dect = find_module(module_name, [plugin_path])
					try:
						module_obj = load_module(module_name, file_handle, file_path, dect)
						#logging.info("{} loaded.".format(module_name))
					finally:
						if file_handle: file_handle.close()

	# 返回所有的插件
	@property
	def all_plugins(self):
		return self.__all_plugins

	# 注册插件
	def register_all_plugin(self, _plugin):
		plugin_name = '.'.join([_plugin.__module__, _plugin.__name__])
		plugin_obj = _plugin()
		self.__all_plugins[plugin_name] = plugin_obj

	# 注销插件
	def unregister_plugin(self, plugin_name):
		if plugin_name in self.__all_plugins:
			plugin_obj = self.__all_plugins[plugin_name]
			del plugin_obj

	# 获取插件对象。
	def get_plugin_object(self, plugin_name=None):
		if plugin_name is None:
			return self.__all_plugins.values()
		else:
			result = self.__all_plugins[plugin_name] if plugin_name in self.__all_plugins else None
			return result

	# 根据插件名字，获取插件对象。（提供插件之间的通信）
	@staticmethod
	def get_plugin_by_name(plugin_name):
		if plugin_name is None:
			return None
		else:
			for single_model in __ALLMODEL__:
				plugin = single_model.get_plugin_object(plugin_name)
				if plugin:
					return plugin


# 插件框架的接入点。便于管理各个插件。各个插件通过继承接入点类，利用Python中metaclass的优势，将插件注册。接入点中定义了各个插件模块必须要实现的接口。
class ModelComponent(object):
	__metaclass__ = PluginManager

	def start(self):
		print 'Module {} Please write the start() function'.format(self.__class__)


class ModelTask(object):
	__metaclass__ = PluginManager

	def start(self):
		print 'Module {} Please write the start() function'.format(self.__class__)

	def changelanguage(self, language):
		print 'please write the changelanguage() function'


__ALLMODEL__ = (ModelComponent, ModelTask)
