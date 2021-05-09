# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
# from isupport.tools import print_out


class UType(Document):
	def validate(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Only Administrator can edit this document"))
	
	def on_trash(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Only Administrator can delete this document"))



@frappe.whitelist()
def get_roles():
	query = """ 
		SELECT
			name as role, role_name, disabled, desk_access
		FROM
			`tabRole`
		WHERE
			name NOT IN ('Administrator', 'All', 'Guest') AND disabled = 0
		"""
	roles = frappe.db.sql(query,as_dict=True)
	roles_list =[]
	for role in roles:
		roles_list.append(role.role_name)

	return roles_list



@frappe.whitelist()
def get_allowed_roles(type_name):
	type_doc = frappe.get_doc("UType",type_name)
	
	if type_doc.enable_all_roles:
		return get_roles(), type_doc.enable_all_roles
	else :
		roles_list = []
		for role in type_doc.roles:
			if role.enable:
				roles_list.append(role.role)
		return roles_list , type_doc.enable_all_roles



@frappe.whitelist()
def get_modules():
	from frappe.config import get_modules_from_all_apps
	module_list = [m.get("module_name") for m in get_modules_from_all_apps()]
	return module_list



@frappe.whitelist()
def get_allowed_modules(type_name):
	type_doc = frappe.get_doc("UType",type_name)
	
	if type_doc.enable_all_modules:
		return get_modules(), type_doc.enable_all_modules
	else :
		module_list = []
		for module in type_doc.modules:
			if module.enable:
				module_list.append(module.module)
		return module_list , type_doc.enable_all_modules



@frappe.whitelist()
def get_all_restricted_roles():
	query = """ 
		SELECT
			DISTINCT role
		FROM
			`tabRolesT`
		"""
	roles = frappe.db.sql(query,as_dict=True)
	roles_list =[]
	for role in roles:
		roles_list.append(role.role)
	return roles_list