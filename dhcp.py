#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Marc Ramiro, John W. Flores
# Web API v1.2.1
# Create, delete, modify networks and ranges from Infoblox.
# v1.0 - September 2016

# Input file format:

# ~~~~~~~> NETWORK
# ADD network CIDR [template] # ~~> ADD a new network
# DELETE network CIDR # ~~> Baja de red DHCP
# MODIFY network CIDR | comment$:text;members$:IP%name%fqdn$/IP2%name2%type2;options$:option_name%option_value$/option_name2/option_value2
# e.g:
# MODIFY network 10.58.1.0/25 | comment$:test;members$:172.31.1.1%infoblox.localdomain%dhcpmember$/172.31.1.2%infoblox_2.lab.es%dhcpmember options$:dhcp-lease-time%43200$/domain-name-servers%10.113.1.1,10.242.2.2$/domain-name%test.es$/routers%10.58.1.1
# MODIFY network 10.58.1.0/25 | comment$:test;options$:dhcp-lease-time%36000

# ~~~~~~~> RANGE
# ADD range start_addr end_addr [template]  # ~~> Alta nuevo rango DHCP
# DELETE range start_addr end_addr
# MODIFY range start_addr end_addr | name$:ex_name;comment$:ex_comment;members$:IP%name%type$/IP2%name2%type2;options$:option_name%option_value$/option_name2/option_value2
# e.g:
# MODIFY range 10.58.0.10 10.58.0.126 | failover_association$:test_failover server_association_type$:FAILOVER options$:tftp-server-ip-address%10.16.204.4$/dhcp-lease-time%43200
# MODIFY range 10.58.0.10 10.58.0.126 | options$:tftp-server-ip-address%10.16.204.4$/dhcp-lease-time%43200

import sys, os
from infoblox.common.connection import Infoblox_Connection
from infoblox.common.rollback import Rollback
from infoblox.common.log import Log
from infoblox.dhcp.network import Network
from infoblox.dhcp.range import Range

def get_options(options):
	options_list = []
	options = options.split('$/')
	for option in options:
		opt = option.split('%')
		options_list.append({'name':opt[0],'value':opt[1]})
	return options_list

def get_members(members):
	members_list = []
	members = members.split('$/')
	for member in members:
		member_options = member.split('%')
		members_list.append({'ipv4addr':member_options[0],'name':member_options[1],'_struct':member_options[2]})
	return members_list

def prepare_fields(options):
	f = {}
	print options
	for option in options:
		opt = option.split('$:')
		option_type = opt[0]
		values = opt[1]
		if values.isdigit():
			values = int(values)
		if option_type == 'members':
			values = get_members(opt[1])
		elif option_type == 'options':
			values = get_options(opt[1])
		f[option_type] = values
	return f

def do_work(code, work_type):

	# Setting up the environment
	if work_type == 'default':
		filename = code + '_DHCP.txt'
		log = Log(code, 'DHCP')
		rollback = Rollback(code, 'DHCP')
	elif work_type == 'rollback':
		filename = code + '_DHCP_ROLLBACK.txt'
		log = Log(code, 'DHCP_ROLLBACK')
		rollback = Rollback(code, 'ROLLBACK')

	file_content = get_file_content(filename)

	# If the file does not exist
	if file_content == 1:
		print(filename + ' not found.')
		return False
	# If the file is empty
	elif len(file_content) < 1:
		print(filename + ' is empty!')
		return False

	infoblox_connection = Infoblox_Connection()
	dhcp_network = Network(log, rollback, infoblox_connection)
	dhcp_range = Range(log, rollback, infoblox_connection)

	for line in file_content:
		log.add_message(line)
		instruction = line[0].split(' ')
		action = instruction[0]
		i_type = instruction[1]

		if i_type == 'network':
			cidr = instruction[2]
			if action == 'ADD':
				if len(instruction) > 3:
					template = instruction[3]
					dhcp_network.add(cidr, template)
				else:
					dhcp_network.add(cidr)
			elif action == 'DELETE':
				# If we delete a network, we have to remember that it may have ranges
				range_ref = dhcp_range.get_reference(cidr=cidr, multiple=True)
				# If it has any range
				if range_ref:
					backup_range = ''
					# We have to generate their rollback instructions
					for r in range_ref:
						backup_range += dhcp_range.do_backup('ADD', reference=r)
						backup_range += dhcp_range.do_backup('MODIFY', reference=r)
					# Now we can delete the network
					dhcp_network.delete(cidr)
					# Finally, the instructions to restore the ranges are written in the file
					rollback.add_instruction(backup_range)
			elif action == 'MODIFY':
				options = ''
				# All the options are specified after the '|' character
				line = line.split(' | ')
				# If options are found
				if len(line) > 1:
					# Each option is delimited by the ';' character
					options = line[1].split(';')
				if options != '':
					fields = prepare_fields(options)
					dhcp_network.modify(cidr, fields)
				else:
					log.add_result('No options specified!', 'error')
		elif i_type == 'range':
			start_addr = instruction[2]
			end_addr = instruction[3]
			if action == 'ADD':
				if len(instruction) > 4:
					template = instruction[4]
					dhcp_range.add(start_addr, end_addr, template=template)
				else:
					dhcp_range.add(start_addr, end_addr)
			elif action == 'DELETE':
				dhcp_range.delete(start_addr=start_addr, end_addr=end_addr)
			elif action == 'MODIFY':
				options = ''
				line = line.split(' | ')
				# Si tenemos opciones
				if len(line) > 1:
					options = line[1].split(';')
				if options != '':
					fields = prepare_fields(options)
					dhcp_range.modify(start_addr, end_addr, fields)
				else:
					log.add_result('No options specified!', 'error')
	rollback.create_file()
	log.create_file()

def get_file_content(filename):

	''' Read a file and store it's content in memory
	Arguments:
		~~> filename: path to the file

    Return:
	OK: Array
	NOK: 1 '''

	# If the file exists
	if os.path.isfile(filename):
		with open(filename, 'r') as f_in:
			lines = (line.rstrip() for line in f_in)
			lines = list(line for line in lines if line) # Non-blank lines in a list
		return lines
	else:
		return 1

if __name__ == '__main__':
	if len(sys.argv) == 2:
		code = sys.argv[1]
		do_work(code, 'default')
	elif len(sys.argv) == 3:
		if sys.argv[1] == 'rollback':
			code = sys.argv[2]
			do_work(code, 'rollback')
