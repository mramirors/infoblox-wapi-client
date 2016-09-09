#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Marc Ramiro, John W. Flores
# Web API v1.2.1
# Create, delete, modify dns records from Infoblox.
# Create and delete zone delegations and zone forwards.
# v1.0 - September 2016

# Input file format:

# ~~~~~~~> RECORD A
# ADD|DELETE A DIRECT LAN fqdn IP # ~~> A
# ADD|DELETE A REVERSE LAN fqdn IP # ~~> PTR
# ADD|DELETE A BOTH LAN fqdn IP # ~~> A + PTR
# MODIFY A BOTH LAN fqdn_new IP_new fqdn_old IP_old
# ~~~~~~~> RECORD CNAME
# ADD|DELETE C LAN fqdn canonical
# MODIFY C LAN fqdn_new canonical_new fqdn_old canonical_old
# ~~~~~~~> RECORD MX
# ADD|DELETE M LAN fqdn mail_server preference
# ~~~~~~~> RECORD TXT
# ADD|DELETE T LAN fqdn text  ---> IMPORTANTE: EL TEXTO TIENE QUE IR SIN COMILLAS!!
# ~~~~~~~> RECORD SRV
# ADD|DELETE S LAN fqdn preference weight port target
# ~~~~~~~> Delegation
# ADD|DELETE D LAN fqdn fqdn_server IP_server fqdn_Nserver IPNserver
# ~~~~~~~> Forward
# ADD|DELETE F LAN fqdn fqdn_server IP_server fqdn_Nserver IPNserver | fqdn_member fqdn_member2 # ~~> Forward -> La barra (|) sirve para delimitar los servidores a los que se hace el forward, de los servidores desde los cuales se envia

import sys, os
from infoblox.common.connection import Infoblox_Connection
from infoblox.common.utils import get_infoblox_view
from infoblox.common.rollback import Rollback
from infoblox.common.log import Log
from infoblox.dns.records import Record_A, Record_PTR, Record_CNAME, Record_MX, Record_TXT, Record_SRV, Delegated, Forwarded

def do_work(codigo_cambio, work_type):

	# Setting up the environment
	if work_type == 'normal':
		filename = codigo_cambio + '_DNS.txt'
		log = Log(codigo_cambio, 'DNS')
		rollback = Rollback(codigo_cambio, 'DNS')
	elif work_type == 'rollback':
		filename = codigo_cambio + '_DNS_ROLLBACK.txt'
		log = Log(codigo_cambio, 'DNS_ROLLBACK')
		rollback = Rollback(codigo_cambio, 'ROLLBACK')

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

	for line in file_content:
		log.add_message(line)
		instruction = line.split(' ')
		action = instruction[0]
		i_type = instruction[1]

		if i_type == 'A':
			d_type = instruction[2]
			view = get_infoblox_view(instruction[3])
			fqdn = instruction[4]
			ip = instruction[5]
			if d_type == 'DIRECT':
				record_a = Record_A(log, rollback, infoblox_connection)
				if action == 'ADD':
					record_a.add(fqdn, ip, view)
				elif action == 'DELETE':
					record_a.delete(fqdn, ip, view)
				elif action == 'MODIFY':
					fqdn_old = instruction[6]
					ip_old = instruction[7]
					record_a.modify(fqdn, ip, fqdn_old, ip_old, view)
			elif d_type == 'REVERSE':
				record_ptr = Record_PTR(log, rollback, infoblox_connection)
				if action == 'ADD':
					record_ptr.add(fqdn, ip, view)
				elif action == 'DELETE':
					record_ptr.delete(fqdn, ip, view)
				elif action == 'MODIFY':
					fqdn_old = instruction[6]
					ip_old = instruction[7]
					record_ptr.modify(fqdn, ip, fqdn_old, ip_old, view)
			elif d_type == 'BOTH':
				record_a = Record_A(log, rollback, infoblox_connection)
				if action == 'ADD':
					record_a.add(fqdn, ip, view)
				elif action == 'DELETE':
					record_a.delete(fqdn, ip, view)
				elif action == 'MODIFY':
					fqdn_old = instruction[6]
					ip_old = instruction[7]
					record_a.modify(fqdn, ip, fqdn_old, ip_old, view)
				record_ptr = Record_PTR(log, rollback, infoblox_connection)
				if action == 'ADD':
					record_ptr.add(fqdn, ip, view)
				elif action == 'DELETE':
					record_ptr.delete(fqdn, ip, view)
				elif action == 'MODIFY':
					fqdn_old = instruction[6]
					ip_old = instruction[7]
					record_ptr.modify(fqdn, ip, fqdn_old, ip_old, view)
		elif i_type == 'C':
			view = get_infoblox_view(instruction[2])
			name = instruction[3]
			canonical = instruction[4]
			record_cname = Record_CNAME(log, rollback, infoblox_connection)
			if action == 'ADD':
				record_cname.add(name, canonical, view)
			elif action == 'DELETE':
				record_cname.delete(name, canonical, view)
			elif action == 'MODIFY':
				name_old = instruction[5]
				canonical_old = instruction[6]
				record_cname.modify(name, canonical, name_old, canonical_old, view)
		elif i_type == 'M':
			view = get_infoblox_view(instruction[2])
			fqdn = instruction[3]
			mail_exchanger = instruction[4]
			preference = int(instruction[5])
			record_mx = Record_MX(log, rollback, infoblox_connection)
			if action == 'ADD':
				record_mx.add(fqdn, mail_exchanger, preference, view)
			elif action == 'DELETE':
				record_mx.delete(fqdn, mail_exchanger, preference, view)
		elif i_type == 'T':
			view = get_infoblox_view(instruction[2])
			fqdn = instruction[3]
			text = ' '.join(instruction[4:])
			record_txt = Record_TXT(log, rollback, infoblox_connection)
			if action == 'ADD':
				record_txt.add(fqdn, text, view)
			elif action == 'DELETE':
				record_txt.delete(fqdn, text, view)
		elif i_type == 'S':
			view = get_infoblox_view(instruction[2])
			fqdn = instruction[3]
			preference = int(instruction[4])
			peso = int(instruction[5])
			puerto = int(instruction[6])
			target = instruction[7]
			record_srv = Record_SRV(log, rollback, infoblox_connection)
			if action == 'ADD':
				record_srv.add(fqdn, preference, peso, puerto, target, view)
			elif action == 'DELETE':
				record_srv.delete(fqdn, preference, peso, puerto, target, view)
		elif i_type == 'D':
			view = get_infoblox_view(instruction[2])
			fqdn = instruction[3]
			delegated = Delegated(log, rollback, infoblox_connection)
			if action == 'ADD':
				servers = instruction[4:]
				l_servers = [] # ~~> Lista de diccionarios con los servidores
				for i in range(0, len(servers), 2):
					l_servers.append({'name':servers[i], 'address':servers[i+1]})
				delegated.add(fqdn, l_servers, view)
			elif action == 'DELETE':
				delegated.delete(fqdn, view)
		elif i_type == 'F':
			view = get_infoblox_view(instruction[2])
			fqdn = instruction[3]
			forwarded = Forwarded(log, rollback, infoblox_connection)
			if action == 'ADD':
				x = instruction.index('|')
				servers = instruction[4:x]
				members = instruction[x+1:]
				l_servers = [] # ~~> Lista de diccionarios con los servidores
				l_members = []
				for i in range(0, len(servers), 2):
					l_servers.append({'name':servers[i], 'address':servers[i+1]})
				for m in members:
					l_members.append({'name':m})
				forwarded.add(fqdn, l_servers, l_members, view)
			elif action == 'DELETE':
				forwarded.delete(fqdn, view)
		else:
			log.add_result('Instruction format', 'error')
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
		codigo_cambio = sys.argv[1]
		do_work(codigo_cambio, 'normal')
	elif len(sys.argv) == 3:
		if sys.argv[1] == 'rollback':
			codigo_cambio = sys.argv[2]
			do_work(codigo_cambio, 'rollback')
