# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
import os
from isupport.tools import print_out

class ISupportSettings(Document):
	
	def validate(self):
		self.update_support_email()
	

	def update_support_email(self):
		with open(frappe.get_site_path('site_config.json'), "r") as jsonFile:
			data = json.load(jsonFile)
		if self.support_email:
			# tmp = data["error_report_email"]
			data["error_report_email"] = self.support_email
			with open(frappe.get_site_path('site_config.json'), "w") as jsonFile:
				json.dump(data, jsonFile)