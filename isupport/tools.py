# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
from frappe.utils import flt
import frappe
import traceback



def print_out(message, alert= False, add_traceback=False, to_error_log=False ):
	if not message:
		return	
	
	def out(mssg):
		if message:
			frappe.errprint(str(mssg))
			if to_error_log:
				frappe.log_error(str(mssg))
			if add_traceback:
				if len(frappe.utils.get_traceback()) > 20:
					frappe.errprint(frappe.utils.get_traceback())
			if alert:
				frappe.msgprint(str(mssg))

	def check_msg(msg):
		if isinstance(msg, str):
			msg = str(msg)

		elif isinstance(msg, int):
			msg = str(msg)

		elif isinstance(msg, float):
			msg = str(msg)

		elif isinstance(msg, dict):
			msg = frappe._dict(msg)
			
		elif isinstance(msg, list):
			for item in msg:
				check_msg(item)
			msg = ""

		elif isinstance(msg, object):
			msg = str(msg.__dict__)
		
		else:
			msg = str(msg)
		out(msg)


	check_msg(message)
