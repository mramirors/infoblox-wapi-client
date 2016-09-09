#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

class Rollback(object):
	''' Rollback class	'''
	def __init__(self, op_code, obj_type):
		'''
		Arguments:
			~~> op_code: String representing the operation code.
			~~> obj_type: String representing the type of object (DNS, DHCP, etc)
		'''
		self.op_code = op_code
		self.obj_type = obj_type
		self.content = list()

	def add_instruction(self, instruction):
		''' Add an instruction into the list.
		Arguments:
			~~> instruction: Rollback instruction
		'''
		if self.obj_type != 'ROLLBACK':
			self.content.append(instruction)

	def create_file(self):
		''' Dump the instructions from the list to a file '''
		if self.obj_type != 'ROLLBACK':
			rollback_file = open(self.op_code + '_' + self.obj_type +'_ROLLBACK.txt', 'w')
			for values in self.content:
				rollback_file.write(values)
			rollback_file.close()
