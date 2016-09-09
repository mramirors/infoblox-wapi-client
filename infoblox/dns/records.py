#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

from infoblox.common.infoblox_object import Infoblox_Object
from infoblox.common.utils import get_ch_view

class Record_A(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Record_A, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, d_type, reference='', fqdn='', ip='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(reference['view'])
			if rb_action == 'ADD':
				rb_instruction = 'ADD A %s %s %s %s\n' %(d_type, view, reference['name'], reference['ipv4addr'])
			elif rb_action == 'MODIFY':
				rb_instruction = 'MODIFY A %s %s %s %s %s %s\n' %(d_type, view, reference['name'], reference['ipv4addr'], fqdn, ip)
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE A %s %s %s %s\n' %(d_type, view, fqdn, ip)

		return rb_instruction

	def get_reference(self, fqdn, ip, view):

		f = 'view=%s&name=%s&ipv4addr=%s&_return_fields=view,name,ipv4addr,ttl' %(view, fqdn, ip)

		try:
			reference = self.connection.perform_request('GET', object_type='record:a', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, ip, view):

		rb_instruction = self.do_backup('DELETE', 'DIRECT', fqdn=fqdn, ip=ip, view=view)

		fields = {'name':fqdn, 'ipv4addr':ip, 'view': view}

		response = self.connection.perform_request('POST', object_type='record:a',\
				content_type='application/json', fields=fields)

		if 'record:a/' in response:
			self.log.add_result("Record A '%s' -> '%s' added in '%s' view." %(fqdn, ip, view), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self, fqdn, ip, fqdn_old, ip_old, view):

		reference = self.get_reference(fqdn_old, ip_old, view)

		if reference:
			fields = {'name':fqdn, 'ipv4addr':ip}
			rb_instruction = self.do_backup('MODIFY', 'DIRECT', reference, fqdn, ip, view)
			response = self.connection.perform_request('PUT', ref=reference['_ref'],\
						content_type='application/json', fields=fields)

			if 'record:a/' in response:
				self.log.add_result("Record A '%s' -> '%s' updated in '%s' view." %(fqdn, ip, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record A '%s' -> '%s' doesn't exist in '%s' view." %(fqdn_old, ip_old, view), 'error')
			return 0

	def delete(self, fqdn, ip, view):

		reference = self.get_reference(fqdn, ip, view)

		if reference:
			rb_instruction = self.do_backup('ADD', 'DIRECT', reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])
			if 'record:a/' in response:
				self.log.add_result("Record A '%s' -> '%s' deleted in '%s' view." %(fqdn, ip, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record A '%s' -> '%s' doesn't exist in '%s' view." %(fqdn, ip, view), 'error')
			return 0

class Record_PTR(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Record_PTR, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, d_type, reference='', fqdn='', ip='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(reference['view'])
			if rb_action == 'ADD':
				rb_instruction = 'ADD A %s %s %s %s\n' %(d_type, view, reference['ptrdname'], reference['ipv4addr'])
			elif rb_action == 'MODIFY':
				rb_instruction = 'MODIFY A %s %s %s %s %s %s\n' %(d_type, view, reference['ptrdname'], reference['ipv4addr'], fqdn, ip)
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE A %s %s %s %s\n' %(d_type, view, fqdn, ip)

		return rb_instruction

	def get_reference(self, fqdn, ip, view):

		f = 'view=%s&ptrdname=%s&ipv4addr=%s&_return_fields=view,ptrdname,ipv4addr,ttl' %(view, fqdn, ip)

		try:
			reference = self.connection.perform_request('GET', object_type='record:ptr', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, ip, view):

		rb_instruction = self.do_backup('DELETE', 'REVERSE', fqdn=fqdn, ip=ip, view=view)

		fields = {'ptrdname':fqdn, 'ipv4addr':ip, 'view': view}

		response = self.connection.perform_request('POST', object_type='record:ptr',\
				content_type='application/json', fields=fields)

		if 'record:ptr/' in response:
			self.log.add_result("Record PTR '%s' -> '%s' added in '%s' view." %(ip, fqdn, view), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self, fqdn, ip, fqdn_old, ip_old, view):

		reference = self.get_reference(fqdn_old, ip_old, view)

		if reference:
			fields = {'ptrdname':fqdn, 'ipv4addr':ip}
			rb_instruction = self.do_backup('MODIFY', 'REVERSE', reference, fqdn, ip, view)
			response = self.connection.perform_request('PUT', ref=reference['_ref'],\
						content_type='application/json', fields=fields)

			if 'record:ptr/' in response:
				self.log.add_result("Record PTR '%s' -> '%s' updated in '%s' view." %(fqdn, ip, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record PTR '%s' -> '%s' doesn't exist in '%s' view." %(fqdn_old, ip_old, view), 'error')
			return 0

	def delete(self, fqdn, ip, view):

		reference = self.get_reference(fqdn, ip, view)

		if reference:
			rb_instruction = self.do_backup('ADD', 'REVERSE', reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'record:ptr/' in response:
				self.log.add_result("Record PTR '%s' -> '%s' deleted in '%s' view." %(ip, fqdn, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record PTR '%s' -> '%s' doesn't exist in '%s' view." %(ip, fqdn, view), 'error')
			return 0

class Record_CNAME(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Record_CNAME, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, reference='', name='', canonical='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(reference['view'])
			if rb_action == 'ADD':
				rb_instruction = 'ADD C %s %s %s\n' %(view, reference['name'], reference['canonical'])
			elif rb_action == 'MODIFY':
				rb_instruction = 'MODIFY C %s %s %s %s %s\n' %(view, reference['name'], reference['canonical'], name, canonical)
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE C %s %s %s\n' %(view, name, canonical)

		return rb_instruction

	def get_reference(self, name, canonical, view):

		f = 'view=%s&name=%s&canonical=%s&_return_fields=view,name,canonical,ttl' %(view, name, canonical)

		try:
			reference = self.connection.perform_request('GET', object_type='record:cname', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, name, canonical, view):

		rb_instruction = self.do_backup('DELETE', name=name, canonical=canonical, view=view)

		fields = {'name':name, 'canonical':canonical, 'view': view}

		response = self.connection.perform_request('POST', object_type='record:cname',\
				content_type='application/json', fields=fields)

		if 'record:cname/' in response:
			self.log.add_result("Record CNAME '%s' -> '%s' added in '%s' view." %(name, canonical, view), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self, name, canonical, name_old, canonical_old, view):

		reference = self.get_reference(name_old, canonical_old, view)

		if reference:
			fields = {'name':name, 'canonical':canonical}

			rb_instruction = self.do_backup('MODIFY', reference=reference, name=name, canonical=canonical, view=view)

			response = self.connection.perform_request('PUT', ref=reference['_ref'],\
						content_type='application/json', fields=fields)

			if 'record:cname/' in response:
				self.log.add_result("Record CNAME '%s' -> '%s' updated in '%s' view." %(name, canonical, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record CNAME '%s' -> '%s' doesn't exist in '%s' view." %(name_old, canonical_old, view), 'error')
			return 0

	def delete(self, name, canonical, view):

		reference = self.get_reference(name, canonical, view)

		if reference:
			rb_instruction = self.do_backup('ADD', reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'record:cname/' in response:
				self.log.add_result("Record CNAME '%s' -> '%s' deleted in '%s' view." %(name, canonical, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record CNAME '%s' -> '%s' doesn't exist in '%s' view." %(name, canonical, view), 'error')
			return 0

class Record_MX(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Record_MX, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, reference='', fqdn='', mail_exchanger='', preference='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(reference['view'])
			if rb_action == 'ADD':
				rb_instruction = 'ADD M %s %s %s %s\n' %(view, reference['name'], reference['mail_exchanger'], reference['preference'])
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE M %s %s %s %s\n' %(view, fqdn, mail_exchanger, preference)

		return rb_instruction

	def get_reference(self, fqdn, mail_exchanger, preference, view):

		f = 'view=%s&name=%s&mail_exchanger=%s&preference=%s&_return_fields=view,name,mail_exchanger,preference,ttl' %(view, fqdn, mail_exchanger, preference)

		try:
			reference = self.connection.perform_request('GET', object_type='record:mx', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, mail_exchanger, preference, view):

		rb_instruction = self.do_backup('DELETE', fqdn=fqdn, mail_exchanger=mail_exchanger, preference=preference, view=view)

		fields = {'name':fqdn, 'mail_exchanger':mail_exchanger, 'preference':preference, 'view': view}

		response = self.connection.perform_request('POST', object_type='record:mx',\
				content_type='application/json', fields=fields)

		if 'record:mx/' in response:
			self.log.add_result("Record MX '%s' -> '%s' with preference %s added in '%s' view." %(fqdn, mail_exchanger, preference, view), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self):
		pass

	def delete(self, fqdn, mail_exchanger, preference, view):

		reference = self.get_reference(fqdn, mail_exchanger, preference, view)

		if reference:
			rb_instruction = self.do_backup('ADD', reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'record:mx/' in response:
				self.log.add_result("Record MX '%s' -> '%s' with preference %s deleted in '%s' view." %(fqdn, mail_exchanger, preference, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record MX '%s' -> '%s' with preference %s doesn't exist in '%s' view." %(fqdn, mail_exchanger, preference, view), 'error')
			return 0

class Record_TXT(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Record_TXT, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, reference='', fqdn='', text='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(reference['view'])
			if rb_action == 'ADD':
				rb_instruction = 'ADD T %s %s %s\n' %(view, reference['name'], reference['text'])
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE T %s %s %s\n' %(view, fqdn, text)

		return rb_instruction

	def get_reference(self, fqdn, text, view):

		f = 'view=%s&name=%s&text=%s&_return_fields=view,name,text,ttl' %(view, fqdn, text)

		try:
			reference = self.connection.perform_request('GET', object_type='record:txt', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, text, view):
		rb_instruction = self.do_backup('DELETE', fqdn=fqdn, text=text, view=view)
		text = '"%s"' %(text)

		fields = {'name':fqdn, 'text':text, 'view': view}

		response = self.connection.perform_request('POST', object_type='record:txt',\
				content_type='application/json', fields=fields)

		if 'record:txt/' in response:
			self.log.add_result("Record TXT '%s' with text %s added in '%s' view." %(fqdn, text, view), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self):
		pass

	def delete(self, fqdn, text, view):
		text = '"%s"' %(text)
		reference = self.get_reference(fqdn, text, view)

		if reference:
			rb_instruction = self.do_backup('ADD', reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'record:txt/' in response:
				self.log.add_result("Record TXT '%s' with text %s deleted in '%s' view." %(fqdn, text, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record TXT '%s' with text %s doesn't exist in '%s' view." %(fqdn, text, view), 'error')
			return 0

class Record_SRV(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Record_SRV, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, reference='', fqdn='', preference='', weight='', port='', target='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(reference['view'])
			if rb_action == 'ADD':
				rb_instruction = 'ADD S %s %s %s %s %s %s\n' %(view, reference['name'], reference['priority'], reference['weight'], reference['port'], reference['target'])
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE S %s %s %s %s %s %s\n' %(view, fqdn, preference, weight, port, target)

		return rb_instruction

	def get_reference(self, fqdn, preference, weight, port, target, view):

		f = 'view=%s&name=%s&priority=%s&weight=%s&port=%s&target=%s&_return_fields=view,name,priority,weight,port,target,ttl' %(view, fqdn, preference, weight, port, target)

		try:
			reference = self.connection.perform_request('GET', object_type='record:srv', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, preference, weight, port, target, view):
		rb_instruction = self.do_backup('DELETE', fqdn=fqdn, preference=preference, weight=weight, port=port, target=target, view=view)

		fields = {'name':fqdn, 'priority':preference, 'weight':weight, 'port':port, 'target':target, 'view': view}

		response = self.connection.perform_request('POST', object_type='record:srv',\
				content_type='application/json', fields=fields)

		if 'record:srv/' in response:
			self.log.add_result("Record SRV '%s' with priority '%s', weight '%s', port '%s' and target '%s' added in '%s' view." %(fqdn, preference, weight, port, target, view), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self):
		pass

	def delete(self, fqdn, preference, weight, port, target, view):
		reference = self.get_reference(fqdn, preference, weight, port, target, view)

		if reference:
			rb_instruction = self.do_backup('ADD', reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'record:srv/' in response:
				self.log.add_result("Record SRV '%s' with priority '%s', weight '%s', port '%s' and target '%s' deleted in '%s' view." %(fqdn, preference, weight, port, target, view), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Record SRV '%s' with priority '%s', weight '%s', port '%s' and target '%s' doesn't exist in '%s' view." %(fqdn, preference, weight, port, target, view), 'error')
			return 0

class Delegated(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Delegated, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, reference='', fqdn='', servers='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(view)
			if rb_action == 'ADD':
				rb_instruction = 'ADD D %s %s' %(view, fqdn)
				servers = reference
				for s in servers:
					rb_instruction += ' %s %s' %(s.get('name'), s.get('address'))
				rb_instruction += '\n'
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE D %s %s\n' %(view, fqdn)

		return rb_instruction

	def get_reference(self, fqdn, view):

		f = 'view=%s&fqdn=%s&_return_fields=delegate_to' %(view, fqdn)
		try:
			reference = self.connection.perform_request('GET', object_type='zone_delegated', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, servers, view):
		rb_instruction = self.do_backup('DELETE', fqdn=fqdn, view=view)

		fields = {'fqdn':fqdn, 'delegate_to':servers, 'view': view}

		response = self.connection.perform_request('POST', object_type='zone_delegated',\
				content_type='application/json', fields=fields)
		if 'zone_delegated/' in response:
			self.log.add_result("Zone %s delegated" %(fqdn), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self):
		pass

	def delete(self, fqdn, view):
		reference = self.get_reference(fqdn, view)

		if reference:
			rb_instruction = self.do_backup('ADD', fqdn=fqdn, view=view, reference=reference['delegate_to'])
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'zone_delegated/' in response:
				self.log.add_result("Zone %s removed." %(fqdn), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Zone %s is not delegated" %(fqdn), 'error')
			return 0

class Forwarded(Infoblox_Object):

	def __init__(self, log, rollback, infoblox_connection):
		super(Forwarded, self).__init__(log, rollback, infoblox_connection)

	def do_backup(self, rb_action, reference='', fqdn='', view=''):

		rb_instruction = ''

		if reference:
			view = get_ch_view(view)
			if rb_action == 'ADD':
				rb_instruction = 'ADD F %s %s' %(view, fqdn)
				servers = reference['forward_to']
				for s in servers:
					rb_instruction += ' %s %s' %(s.get('name'), s.get('address'))
				members = reference['forwarding_servers']
				for m in members:
					rb_instruction += ' %s' %(s.get('name'))
				rb_instruction += '\n'
		else:
			view = get_ch_view(view)
			if rb_action == 'DELETE':
				rb_instruction = 'DELETE F %s %s\n' %(view, fqdn)

		return rb_instruction

	def get_reference(self, fqdn, view):
		f = 'view=%s&fqdn=%s&_return_fields=forward_to,forwarding_servers,forwarders_only' %(view, fqdn)
		try:
			reference = self.connection.perform_request('GET', object_type='zone_forward', fields=f)
			return reference[0]
		except (IndexError, TypeError):
			return None

	def add(self, fqdn, servers, members, view):
		rb_instruction = self.do_backup('DELETE', fqdn=fqdn, view=view)

		fields = {'fqdn':fqdn, 'forward_to':servers, 'forwarding_servers':members, 'forwarders_only':True, 'view': view}

		response = self.connection.perform_request('POST', object_type='zone_forward',\
				content_type='application/json', fields=fields)
		if 'zone_forward/' in response:
			self.log.add_result("Zone %s forwarded." %(fqdn), 'ok')
			self.rollback.add_instruction(rb_instruction)
			return 1
		else:
			self.log.add_result(response, 'error')
			return 0

	def modify(self):
		pass

	def delete(self, fqdn, view):
		reference = self.get_reference(fqdn, view)

		if reference:
			rb_instruction = self.do_backup('ADD', fqdn=fqdn, view=view, reference=reference)
			response = self.connection.perform_request('DELETE', ref=reference['_ref'])

			if 'zone_forward/' in response:
				self.log.add_result("Zone %s removed." %(fqdn), 'ok')
				self.rollback.add_instruction(rb_instruction)
				return 1
			else:
				self.log.add_result(response, 'error')
				return 0
		else:
			self.log.add_result("Zone %s is not forwarded." %(fqdn), 'error')
			return 0
