# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import subprocess
from frappe.utils import getdate, get_last_day, get_first_day, nowdate, date_diff
from frappe import _
from isupport.tools import print_out

class SiteLimitations(Document):
	def validate(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Only Administrator can edit this document"))
		if self.company_allowed < 1 or self.users_allowed < 1 or self.space_allowed < 1 or self.sms_allowed < 1:
			frappe.throw(_("Limitations must be greater than zero"))
		# print_out(str(get_count_type_of_yser()))
		toggole_enable_disable_users(self.end_date, self.ignore_end_date)
	
	def on_trash(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Only Administrator can delete this document"))


	def get_usage_info(self):
		user_list = frappe.get_list('User', filters = {
		'enabled': 1,
		'name': ['not in',['Guest','Administrator']]
		}, page_length = 2000000)
		self.active_users = len(user_list)
		total_size = ""
		output_string = subprocess.check_output(["du","-s","--block-size=1M",frappe.get_site_path()])
		for char in output_string:
			if chr(char) == "\t":
				break
			else:
				total_size += chr(char)

		total_size = int(total_size)

		self.used_space = total_size
		self.active_company = len(frappe.get_all("Company",filters={}))
		
		today = getdate()
		end_day = get_last_day(today)
		start_day = get_first_day(today)
		if self.enable_sms_dates:
			end_day = self.sms_to_date
			start_day = self.sms_from_date
		query = """ 
				SELECT
				COUNT(name)
				FROM
					`tabSMS Log`
				WHERE
					DATE(sent_on) BETWEEN '{start_day}' AND '{end_day}'
				""".format(start_day=start_day,end_day=end_day)
		sms_list = frappe.db.sql(query,as_dict=True)
		sms_count = sms_list[0]['COUNT(name)']

		return [len(user_list),total_size,len(frappe.get_all("Company",filters={})),sms_count]


	def get_count_type_of_user(self):
		query = """ 
				SELECT
				COUNT(type_of_user) as count, type_of_user
				FROM
					`tabUser`
				WHERE
					enabled = 1 AND name != "Administrator" AND name != "Guest" AND name != "Support"
				GROUP BY type_of_user
				"""
		users_types = frappe.db.sql(query,as_dict=True)
		types_info_list = []
		for i in users_types:
			allowed_count = frappe.get_value("UType", i.type_of_user, "allowed")
			type_dict ={
				"type_name": i.type_of_user,
				"allowed_count": allowed_count,
				"active_count": i.count
			}
			types_info_list.append(type_dict)
		return types_info_list



def user_limit(doc, method):
	limitations = frappe.get_single("Site Limitations")
	if not limitations.enable or not limitations.users_restrictions:
		return

	allowed_users = limitations.users_allowed
	user_list = frappe.get_list('User', filters = {
		'enabled': 1,
		'name': ['not in',['Guest','Administrator']]
	}, page_length = 2000000)
	
	contact = frappe.get_value("ISupport Settings",None,"support_email") or "System Administrator"
	
	if len(user_list)>= allowed_users:
		if not frappe.get_list('User', filters={'name': doc.name}):
			frappe.throw('Only {} active users allowed and you have {} active users. Please disable users or to increase the limit please contact {}'. format(allowed_users, len(user_list), contact)) 
		elif doc.enabled == 1 and len(user_list) > allowed_users:
			frappe.throw('Only {} active users allowed and you have {} active users. Please disable users or to increase the limit please contact {}'. format(allowed_users, len(user_list), contact))



def space_limit(doc, method):
	limitations = frappe.get_single("Site Limitations")
	if not limitations.enable or not limitations.space_restrictions:
		return

	allowed_users = limitations.users_allowed
	allowed_space = limitations.space_allowed

	user_list = frappe.get_list('User', filters = {
		'enabled': 1,
		'name': ['not in',['Guest','Administrator']]
		}, page_length = 2000000)
	
	contact = frappe.get_value("ISupport Settings",None,"support_email") or "System Administrator"

	if len(user_list)> allowed_users:
		frappe.throw('Only {} active users allowed and you have {} active users.Please disable users or to increase the limit please contact {}'. format(allowed_users, len(user_list), contact)) 

	total_size = ""
	output_string = subprocess.check_output(["du","-s","--block-size=1M",frappe.get_site_path()])
	for char in output_string:
		if chr(char) == "\t":
			break
		else:
			total_size += chr(char)

	total_size = int(total_size)

	if total_size > allowed_space:
		frappe.throw('You have exceeded your space limit. Delete some files from file manager or to incease the limit please contact system Administrator')




def company_limit(doc, method):
	limitations = frappe.get_single("Site Limitations")
	if not limitations.enable or not limitations.company_restrictions:
		return
	contact = frappe.get_value("ISupport Settings",None,"support_email") or "System Administrator"
	total_company = len(frappe.db.get_all('Company',filters={}))
	if total_company >= limitations.company_allowed:
		if not frappe.get_list('Company', filters={'name': doc.name}):  
			frappe.throw(_("Only {} company allowed and you have {} company.Please remove other company or to increase the limit please contact {}").format(limitations.company_allowed, total_company, contact))



def sms_limit(doc, method=None):
	limitations = frappe.get_single("Site Limitations")
	if not limitations.enable or not limitations.sms_restrictions:
		return

	allowed_sms = limitations.sms_allowed
	today = getdate()
	end_day = get_last_day(today)
	start_day = get_first_day(today)
	if limitations.enable_sms_dates:
			end_day = limitations.sms_to_date
			start_day = limitations.sms_from_date
	query = """ 
            SELECT
               COUNT(name)
            FROM
                `tabSMS Log`
            WHERE
                DATE(sent_on) BETWEEN '{start_day}' AND '{end_day}'
            """.format(start_day=start_day,end_day=end_day)
	sms_list = frappe.db.sql(query,as_dict=True)
	sms_count = sms_list[0]['COUNT(name)']
	contact = frappe.get_value("ISupport Settings",None,"support_email") or "System Administrator"

	if sms_count> allowed_sms:
		frappe.throw('Only {} SMS allowed and you have sent {} SMS. To increase the limit please contact {}'. format(allowed_sms, sms_count, contact)) 


def user_type_limit(doc, method):
	limitations = frappe.get_single("Site Limitations")
	if not limitations.enable or not limitations.enable_users_types_restrictions:
		return

	enable = frappe.get_value("UType",doc.type_of_user,"enable")
	if not enable:
		return
	
	allowed_users = frappe.get_value("UType",doc.type_of_user,"allowed")

	user_list = frappe.get_all('User', filters = {
		'enabled': 1,
		'type_of_user': doc.type_of_user,
		'name': ['not in',['Guest','Administrator','Support']]
	})
	contact = frappe.get_value("ISupport Settings",None,"support_email") or "System Administrator"

	if len(user_list)>= allowed_users:
		if not frappe.get_list('User', filters={'name': doc.name}):
			frappe.throw('Only {} {} active users allowed and you have {} active users. Please disable users or to increase the limit please contact {}'. format(allowed_users, doc.type_of_user, len(user_list), contact)) 
		elif doc.enabled == 1 and len(user_list) > allowed_users:
			frappe.throw('Only {} {} active users allowed and you have {} active users. Please disable users or to increase the limit please contact {}'. format(allowed_users, doc.type_of_user, len(user_list), contact)) 


@frappe.whitelist()
def get_allowed_domains():
	limitations = frappe.get_single("Site Limitations")
	if not limitations.enable or not limitations.domain_restrictions:
		return []
	query = """ 
		SELECT
			domain
		FROM
			`tabAllowed Domains`
		"""
	domains = frappe.db.sql(query,as_dict=True)
	domain_list =[]
	for domain in domains:
		domain_list.append(domain.domain)
	return domain_list 


def toggole_enable_disable_users(end_date=None, ignore_end_date=None):
	def _disable_users(user_list):
		for user in user_list:
			frappe.db.set_value("User",user["name"],"enabled",0, update_modified = False)
			frappe.db.commit()

	def _enable_users(user_list):
		for user in user_list:
			enabled = frappe.get_value("User",user["name"],"enabled")
			if int(enabled) == 0:
				frappe.db.set_value("User",user["name"],"enabled",1, update_modified = False)
				frappe.db.commit()

	if not ignore_end_date and not end_date:
		ignore_end_date = frappe.get_value("Site Limitations",None,"ignore_end_date")
		end_date = frappe.get_value("Site Limitations",None,"end_date")

	user_list = frappe.get_all('User', filters = {
		'name': ['not in',['Guest','Administrator','Support']]
	})

	if int(ignore_end_date) == 1:
		_enable_users(user_list)
		delete_expiry_note()
		
	elif end_date:
		if end_date >= nowdate():
			_enable_users(user_list)
			update_expiry_note(end_date)
	
		elif end_date < nowdate():
			_disable_users(user_list)
			delete_expiry_note()


def update_expiry_note(end_date):
	note_doc = frappe.db.exists("Note", "Notification of Subscription Expiry")
	contact = frappe.get_value("ISupport Settings",None,"support_email") or "System Administrator"
	diff_days = date_diff(end_date,nowdate())

	if diff_days > 31:
		delete_expiry_note()
	else:
		message = "Renewal will be due in {0} days, Please contact {1} for renewal".format(diff_days,contact)
		if note_doc:
			frappe.db.set_value("Note", "Notification of Subscription Expiry","content",message, update_modified = False)
			frappe.db.set_value("Note", "Notification of Subscription Expiry","public",1, update_modified = False)
			frappe.db.set_value("Note", "Notification of Subscription Expiry","notify_on_login",1, update_modified = False)
			frappe.db.set_value("Note", "Notification of Subscription Expiry","notify_on_every_login",1, update_modified = False)
		else:
			note_doc = frappe.new_doc('Note')
			note_doc.title = "Notification of Subscription Expiry"
			note_doc.public = 1
			note_doc.notify_on_login = 1
			note_doc.notify_on_every_login = 1
			note_doc.content = message
			note_doc.insert()


def delete_expiry_note():
	note_doc = frappe.db.exists("Note", "Notification of Subscription Expiry")
	if note_doc:
		frappe.delete_doc("Note", "Notification of Subscription Expiry")
	


def check_end_paln(*args):
	toggole_enable_disable_users()