# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, format_datetime, now, nowdate, getdate, get_url, get_host_name
from frappe.desk.form.utils import add_comment
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils.change_log import get_versions
from isupport.tools import print_out
import requests
import json
from time import sleep

class SupportIssue(Document):
	def validate(self):
		self.set_version()
		self.put_last_message()
		self.add_log()
		self.set_indicator()
		self.add_recipients()
		self.add_transaction_comment()
		self.set_indicator()
		self.clear_transaction_fileds()
		self.make_notification_log()
		self.send_init_sync()
		self.send_changes()




	def add_log(self):
		if not self.is_new():
			if self.notes or self.attached_file or self.error_msg:
				new_log_row = self.append('issue_log', {})
				new_log_row.from_user = frappe.session.user
				new_log_row.from_name = frappe.get_value("User",frappe.session.user,"full_name")
				new_log_row.notes = self.notes
				new_log_row.attached_file = self.attached_file
				new_log_row.date = nowdate()
				new_log_row.time = now()
				new_log_row.error_msg =self.error_msg or ""
				new_log_row.sync = now()
				frappe.db.commit()
				self.send_message()

	
	def clear_transaction_fileds(self):
		self.error_msg = None
		self.include_error = None
		self.attached_file = None
		self.notes = None
		frappe.db.commit()


	
	def make_notification_log(self):
		# if self.notes and frappe.session.user != self.owner_user:
			# alert_doc = frappe.get_doc(self.doctype_name,self.doc_name)
			users = [self.owner, self.modified_by]
			notification_doc = {
				'type': 'Share',
				'document_type': self.doctype,
				'subject': self.notes,
				'document_name': self.name,
				'from_user': frappe.session.user
			}
			enqueue_create_notification(users, notification_doc)


	
	def put_last_message(self):
		space = "\n"
		if self.notes or self.error_msg:
			self.last_message = ""
			if self.notes:
				self.last_message = self.last_message + self.notes + space
				self.last_message = self.last_message + space
			if self.error_msg:
				self.last_message = self.last_message + "Error Log" + space
				self.last_message = self.last_message + "*************" + space
				self.last_message = self.last_message + self.error_msg + space
				self.last_message = self.last_message + space
			self.last_message = self.last_message + _("From : ") + self.edited_user_name + space


	
	def put_messeges(self):
		space = "\n"
		if self.notes:
			if not self.messages:
				self.messages = ""
			self.messages = self.messages + _("From : ") + self.edited_user_name + space
			self.messages = self.messages + space
			self.messages = self.messages + self.notes + space
			self.messages = self.messages + space
			self.messages = self.messages + str(now()) + space
			self.messages = self.messages + space + ("-"*50) + space
			
			

	def set_indicator(self):
		"""Set indicator for portal"""
		if self.status == "Closed":
			self.response_status = "Closed"
		else:
			if getdate(self.due_date) < getdate(nowdate()):
				self.indicator_color = "red"
				self.indicator_title = "Overdue"
				self.response_status = "Overdue"
			else:
				self.indicator_title = "Waiting"
				self.response_status = "Waiting"
	


	def add_recipients(self):
		space = "\n"
		if not self.recipients:
			self.recipients = str()
			self.recipients = self.recipients + str(self.edited_user)
		# if self.transaction_to:
		# 	if self.transaction_to not in self.recipients:
		# 		self.recipients = self.recipients + space + str(self.transaction_to)


	
	def add_transaction_comment(self):
		if not self.is_new():
			if self.notes:
				add_comment(
					self.doctype, 
					self.name,
					self.notes, 
					self.edited_user,
					self.edited_user,
				)

	

	def set_version(self):
		if self.versions:
			return
		version = ""
		space = "\n"
		for key,value in get_versions().items():
			version = version + value["title"] + " " + value["branch"]+" "+value["version"] + space
		self.versions = version
	


	def send_init_sync(self):
		if frappe.session.user == "Guest":
			return
		if self.support_code:
			return
		url = frappe.get_value("ISupport Settings",None,"support_url")
		if not url:
			return
		url = str(url) + "/api/method/usupport.sync.receive_init"
		data = {
			"name": self.name,
			"subject": self.subject,
			"priority": self.priority,
			"versions": self.versions,
			"url": get_host_name(),
			"issue_type": self.issue_type,
			"owner_user": self.owner_user,
			"owner_user_name": self.owner_user_name,
			"issue_date": self.issue_date,
		}
		for i in range(3):
			try:
				r = requests.post(url, data=json.dumps(data), timeout=5)
				r.raise_for_status()
				frappe.logger().debug({"webhook_success": r.text})
				self.support_code = json.loads(r.text)["message"]
				self.need_sync = 0
				self.last_sync = now()
				break
			except Exception as e:
				frappe.logger().debug({"webhook_error": e, "try": i + 1})
				sleep(3 * i + 1)
				if i != 2:
					continue
				else:
					raise e
	


	def send_message(self):
		if frappe.session.user == "Guest":
			return
		if not self.support_code or not self.notes:
			return
		url = frappe.get_value("ISupport Settings",None,"support_url")
		if not url:
			return
		url = str(url) + "/api/method/usupport.sync.receive_message"
		data = {
			"name": self.name,
			"support_code": self.support_code,
			"notes": self.notes,
			"last_message": self.last_message,
			"from_user": frappe.session.user,
			"from_name": frappe.get_value("User",frappe.session.user,"full_name"),
			"date": nowdate(),
			"time": now(),
			"error_msg": self.error_msg or "",
		}
		for i in range(3):
			try:
				r = requests.post(url, data=json.dumps(data), timeout=5)
				r.raise_for_status()
				frappe.logger().debug({"webhook_success": r.text})
				self.need_sync = 0
				self.last_sync = now()
				break
			except Exception as e:
				frappe.logger().debug({"webhook_error": e, "try": i + 1})
				sleep(3 * i + 1)
				if i != 2:
					continue
				else:
					raise e
	


	def send_changes(self):
		if frappe.session.user == "Guest":
			return
		if not self.support_code or self.is_new():
			return
		url = frappe.get_value("ISupport Settings",None,"support_url")
		if not url:
			return
		url = str(url) + "/api/method/usupport.sync.receive_changes"
		data = {
			"name": self.name,
			"support_code": self.support_code,
			"status": self.status,
			"subject": self.subject,
			"priority": self.priority,
			"issue_type": self.issue_type,
			"from_user": frappe.session.user,
			"from_name": frappe.get_value("User",frappe.session.user,"full_name"),
			"date": nowdate(),
			"time": now(),
			"bill_approval": self.bill_approval,
		}
		for i in range(3):
			try:
				r = requests.post(url, data=json.dumps(data), timeout=5)
				r.raise_for_status()
				frappe.logger().debug({"webhook_success": r.text})
				self.need_sync = 0
				self.last_sync = now()
				break
			except Exception as e:
				frappe.logger().debug({"webhook_error": e, "try": i + 1})
				sleep(3 * i + 1)
				if i != 2:
					continue
				else:
					raise e
