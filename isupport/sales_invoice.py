# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import flt
import frappe
from frappe import _


def check_validate_delivery_note(doc=None, method=None, doc_name=None):
	if not doc and doc_name:
		doc = frappe.get_doc("Sales Invoice", doc_name)
		doc.to_save = True
	else:
		doc.to_save = False
	doc.delivery_status = "Not Delivered"
	if doc.update_stock:
		return

	part_delivery = False
	# full_delivery = False
	items_qty = 0
	items_delivered_qty = 0
	i = 0
	for item in doc.items:
		if doc.is_new():
			item.delivery_status = "Not Delivered"
			item.delivered_qty = 0
		items_qty += item.stock_qty
		if item.delivery_note or item.delivered_by_supplier:
			part_delivery = True
			i += 1
		if item.delivered_qty:
			if item.stock_qty == item.delivered_qty:
				item.delivery_status = "Delivered"
			elif item.stock_qty < item.delivered_qty:
				item.delivery_status = "Over Delivered"
			elif item.stock_qty > item.delivered_qty and item.delivered_qty > 0:
				item.delivery_status = "Part Delivered"
			items_delivered_qty += item.delivered_qty
	if i == len(doc.items):
		doc.delivery_status = "Delivered"
	elif doc.to_save and items_delivered_qty >= items_qty:
		doc.delivery_status = "Delivered"
	elif doc.to_save and items_delivered_qty <= items_qty and items_delivered_qty > 0:
		doc.delivery_status = "Part Delivered"
	elif part_delivery:
		doc.delivery_status = "Part Delivered"
	else:
		doc.delivery_status = "Not Delivered"
	if doc.to_save:
		doc.flags.ignore_permissions = True
		doc.save()
        




def check_submit_delivery_note(doc, method):
	if doc.update_stock:
		doc.db_set('delivery_status', "Delivered", commit=True)
		for item in doc.items:
			item.db_set('delivered_qty', item.stock_qty, commit=True)
			item.db_set('delivery_status', "Delivered", commit=True)
	else :
		part_deivery = False
		for item in doc.items:
			if not check_item_is_maintain(item.item_code):
				item.db_set('delivered_qty', item.stock_qty, commit=True)
				item.db_set('delivery_status', "Delivered", commit=True)
				part_deivery = True
		if part_deivery:
			doc.db_set('delivery_status', "Part Delivered", commit=True)



def check_cancel_delivery_note(doc, method):
    if doc.update_stock:
        doc.db_set('delivery_status', "Not Delivered", commit=True)
        for item in doc.items:
            item.db_set('delivered_qty', 0, commit=True)
            item.db_set('delivery_status', "Not Delivered", commit=True)


def update_delivery_on_sales_invoice(doc, method):
    sales_invoice_list = []
    for item in doc.items:
        if item.against_sales_invoice and item.against_sales_invoice not in sales_invoice_list:
            sales_invoice_list.append(item.against_sales_invoice)
    for invoice in sales_invoice_list:
        check_validate_delivery_note(None,None,invoice)


def check_item_is_maintain(item_name):
        is_stock_item = frappe.get_value("Item",item_name,"is_stock_item")
        if is_stock_item != 1:
            return False
        else:
            return True