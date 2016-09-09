#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import json, socket, ssl, requests
from requests import Session, Request
from requests.packages.urllib3.exceptions import InsecureRequestWarning, SNIMissingWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

class Infoblox_Connection(object):
	''' Class used to interact with Infoblox Grid Master '''

	def __init__(self):
		self.id = 'user'
		self.password = 'password'
		self.url = 'https://1.1.1.1/wapi/v1.2.1/'
		self.valid_cert = False
		self.cookie = self.get_cookie()

	def get_cookie(self):
		''' Connect to Infoblox and get the session cookie '''
		try:
			r = requests.get(self.url + 'grid', auth=(self.id, self.password), verify=self.valid_cert)
			results = r.json()
			return r.cookies['ibapauth']
		except ValueError:
			return None

	def perform_request(self, operation, ref='', params='', fields='', \
                                        object_type='', content_type='application/x-www-form-urlencoded'):
		''' Perform requests to Infoblox using the session cookie

		Arguments:
			~~> operation: GET, POST, PUT, DELETE
			~~> ref: infoblox object reference
			~~> params: additional arguments on the request. e.g: _schedinfo.scheduled_time
			~~> fields: data to add/delete/modify/query
			~~> object_type: predefined infoblox object type. e.g:network, record:a
			~~> content_type: JSON, XML, URLENCODED

        Return:
		OK: Dictionary or list of dictionaries
		NOK: Error message '''

		if ref:
			url = self.url + ref
		else:
			url = self.url + object_type

		if params:
			url += '?' + params

		if content_type == 'application/json':
			fields = json.dumps(fields)

		request_cookies = {'ibapauth': self.cookie}
		request_header = {'Content-Type':content_type}

		req = Request(operation, url, data=fields, cookies=request_cookies, headers=request_header)

		s = Session()
		prepped = s.prepare_request(req)
		r = s.send(prepped, verify=self.valid_cert)

		data = r.json()

		if r.status_code >= 200 and r.status_code < 300:
			return data
		else:
			return data['text']
