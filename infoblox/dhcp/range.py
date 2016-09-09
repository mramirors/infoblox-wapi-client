#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

from infoblox.common.infoblox_object import Infoblox_Object

class Range(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Range, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, start_addr='', end_addr='', reference=''):
		''' Look for the range basic configuration and build the rollback instruction

		Arguments:
			~~> rb_action: rollback action
						e.g: If we delete a range our rollback instruction will be to restore it with all its configuration
						e.g: If we add a range, the rollback instruction will be to delete this range. '''

		rb_instruction = ''

		if rb_action == "ADD":
			rb_instruction = 'ADD range %s %s\n' %(reference['start_addr'], reference['end_addr'])
		elif rb_action == "MODIFY":
			rb_instruction = 'MODIFY range %s %s' %(reference['start_addr'], reference['end_addr'])

			rb_instruction += ' | '
			reference.pop('_ref', None)
			for key, value in reference.iteritems():
				if key != 'options':
					rb_instruction += '%s$:%s;' %(key, value)
				else:
					options = []
					for option in value:
						options.append(option['name'] + '%' + option['value'])
					if len(options) > 1:
						rb_instruction +=  '%s$:%s;' %(key, '$/'.join(options))
			if rb_instruction[-1] == ';':
				rb_instruction = rb_instruction[:-1]
			rb_instruction += '\n'

		elif rb_action == 'DELETE':
			if reference:
				rb_instruction = 'DELETE range %s %s\n' %(reference['start_addr'], reference['end_addr'])
			else:
				rb_instruction = 'DELETE range %s %s\n' %(start_addr, end_addr)

		return rb_instruction

	def get_reference(self, cidr='', start_addr='', end_addr='', multiple=False):
		''' Get Infoblox range reference

		Arguments:
			~~> cidr: network CIDR notation
			~~> start_addr: range starting ip address
			~~> end_addr: range last ip address '''
		try:
			if cidr != '':
				f = 'network=%s&_return_fields=start_addr,end_addr,name,comment,options,failover_association,server_association_type' %(cidr)
			elif start_addr != '' and end_addr != '':
				f = 'start_addr=%s&end_addr=%s&_return_fields=start_addr,end_addr,name,comment,options,failover_association,server_association_type' %(cidr)
			reference = self.connection.perform_request('GET', object_type='range', fields=f)
			if not multiple:
				return reference[0]
			else:
				return reference
		except (IndexError, TypeError):
			return None

	def add(self, start_addr, end_addr, template=''):
		''' Create a new range

		Arguments:
			~~> start_addr: network CIDR notation
			~~> end_addr: network CIDR notation
			~~> template: network template (must exist) '''

		rb_instruction = self.do_backup('DELETE', start_addr=start_addr, end_addr=end_addr)
		# Field dictionary
		fields = {"start_addr":start_addr, "end_addr":end_addr}
		#If a network template is specified
		if template:
			fields['template'] = template

		response = self.connection.perform_request('POST', object_type='range',\
					content_type='application/json', fields=fields)

		if 'range/' in response:
			self.log.add_result('Range %s - %s added.' %(start_addr,  end_addr), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self, start_addr, end_addr, fields):
		''' Modify an existing network

		Arguments:
			~~> cidr: network CIDR notation
			~~> fields: fields to modify '''

		reference = self.get_reference(start_addr=start_addr, end_addr=end_addr)

		if reference:
			rb_instruction = self.do_backup('MODIFY', reference=reference)

			response = self.connection.perform_request('PUT', ref=reference['_ref'],\
						content_type='application/json', fields=fields)

			if 'range/' in response:
				self.log.add_result('Range %s - %s updated.' %(reference['start_addr'],  reference['end_addr']), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result('Range does not exist.', 'error')
			return 0

	def delete(self, cidr='', start_addr='', end_addr=''):
		''' Delete an existing range

		Arguments:
			~~> cidr: network CIDR notation
			~~> start_addr: initial ip address for the range
			~~> end_addr: last ip address for the range  '''

		if cidr:
			reference = self.get_reference(cidr=cidr)
		elif start_addr and end_addr:
			reference = self.get_reference(start_addr=start_addr, end_addr=end_addr)

		if reference:
			rb_instruction = self.do_backup('ADD', reference=reference)
			rb_instruction_2 = self.do_backup('MODIFY', reference=reference)

			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'range/' in response:
				self.log.add_result('Range %s - %s deleted.' %(reference['start_addr'],  reference['end_addr']), 'ok')
				self.rollback.add_instruction('%s%s' %(rb_instruction, rb_instruction_2))
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result('Range does not exist.', 'error')
			return 0
