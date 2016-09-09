#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

def get_infoblox_view(view):

	if view == 'LAN':
		return 'default'
	elif view == 'DMZ':
		return 'DMZ'
	elif view == 'Internet':
		return 'Internet'

def get_ch_view(view):

	if view == 'default':
		return 'LAN'
	elif view == 'DMZ':
		return 'DMZ'
	elif view == 'Internet':
		return 'Internet'
