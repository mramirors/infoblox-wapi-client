#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

from abc import ABCMeta, abstractmethod

class Infoblox_Object():
	__metaclass__ = ABCMeta

	def __init__(self, log, rollback, connection):
		self.log = log
		self.rollback = rollback
		self.connection = connection

	@abstractmethod
	def do_backup(self):
		pass

	@abstractmethod
	def get_reference(self):
		pass

	@abstractmethod
	def add(self):
		pass

	@abstractmethod
	def modify(self):
		pass

	@abstractmethod
	def delete(self):
		pass
