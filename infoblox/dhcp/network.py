#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

from infoblox.common.infoblox_object import Infoblox_Object

class Network(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Network, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, cidr, reference=''):
		''' Look for the network basic configuration and build the rollback instruction

		Arguments:
			~~> rb_action: rollback action
						e.g: If we delete a network our rollback instruction will be to restore it with all its configuration
						e.g: If we add a network, the rollback instruction will be to delete this network. '''

		rb_instruction = ''

		if rb_action == 'ADD':
			rb_instruction = 'ADD network %s\n' %(cidr)
		elif rb_action == 'MODIFY':
			rb_instruction = 'MODIFY network %s' %(reference['network'])
			rb_instruction += ' | '
			if 'comment' in reference:
				comment = reference['comment']
				rb_instruction += 'comment$:%s;' %(comment)

			if 'members' in reference:
				members = []
				for member in reference['members']:
					members.append(member['ipv4addr'] + '%' + member['name'] + '%' + member['_struct'])
				if len(members) > 1:
					rb_instruction += 'members$:%s;' %('$/'.join(members))

			if reference['options']:
				options = []
				for option in reference['options']:
					options.append(option['name'] + '%' + option['value'])
				if len(options) > 1:
					rb_instruction +=  'options$:%s' %('$/'.join(options))

			rb_instruction += '\n'

		elif rb_action == 'DELETE':
			rb_instruction = 'DELETE network %s\n' %(cidr)

		return rb_instruction

	def get_reference(self, cidr):
		''' Get Infoblox network reference

		Arguments:
			~~> cidr: network CIDR notation '''
		try:
			f = 'network=%s&_return_fields=network,comment,options,members' %(cidr)
			reference = self.connection.perform_request('GET', object_type='network', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, cidr, template=''):
		''' Create a new network

		Arguments:
			~~> cidr: network CIDR notation
			~~> template: network template (must exist) '''

		rb_instruction = self.do_backup('DELETE', cidr)
		# Field dictionary
		fields = {'network':cidr}
		#If a network template is specified
		if template:
			fields['template'] = template

		response = self.connection.perform_request('POST', object_type='network',\
					content_type='application/json', fields=fields)

		if 'network/' in response:
			self.log.add_result('Network %s added.' %(cidr), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self, cidr, fields):
		''' Modify an existing network

		Arguments:
			~~> cidr: network CIDR notation
			~~> fields: fields to modify '''

		reference = self.get_reference(cidr)

		if reference:
			rb_instruction = self.do_backup('MODIFY',cidr,reference)

			response = self.connection.perform_request('PUT', object_type='network', ref=reference['_ref'],\
						content_type='application/json', fields=fields)

			if 'network/' in response:
				self.log.add_result('Network %s updated.' %(cidr), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result('Network %s does not exist.' %(cidr), 'error')
			return 0

	def delete(self, cidr):
		''' Delete an existing network

		Arguments:
			~~> cidr: network CIDR notation '''

		reference = self.get_reference(cidr)

		if reference:
			rb_instruction = self.do_backup('ADD',cidr)
			rb_instruction_2 = self.do_backup('MODIFY',cidr, reference)

			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'network/' in response:
				self.log.add_result('Network %s deleted.' %(cidr), 'ok')
				self.rollback.add_instruction('%s%s' %(rb_instruction, rb_instruction_2))
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result('Network %s does not exist.' %(cidr), 'error')
			return 0
