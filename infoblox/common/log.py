#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import time

class Log(object):
	''' Basic log class	'''
	# def __init__(self, op_code, obj_type):
	def __init__(self, op_code, obj_type):
		'''
		Arguments:
			~~> op_code: String representing the operation code.
			~~> obj_type: String representing the type of object (DNS, DHCP, etc)
		'''
		self.op_code = op_code
		self.obj_type = obj_type
		self.content = []

	def add_message(self, text):
		''' Add a message into the array '''
		time_date = time.strftime("%a, %d %b %Y %H:%M:%S")
		msg_log = '\n%s ~~> %s\n' %(time_date, text)
		self.content.append(msg_log)

	def add_result(self, result, error_type):
		''' Add the result of the execution '''
		if error_type == 'error':
			msg_log = '\tError: %s\n' %(result)
		elif error_type == 'ok':
			if result:
				msg_log = '\tOK: %s\n' %(result)
			else:
				msg_log = '\tOK\n'
		else:
			msg_log = '\tError: object not found\n'
		self.content.append(msg_log)

	def create_file(self):
		''' Dump content to a file '''
		log_file = open('./logs/' + self.op_code + '_' + self.obj_type +'.log', 'w')
		for msg in self.content:
			log_file.write(msg)
		log_file.close()
