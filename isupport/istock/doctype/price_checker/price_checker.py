# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance, get_stock_value_on
from erpnext import get_company_currency, get_default_company

class PriceChecker(Document):
	pass

@frappe.whitelist()
def get_stock_item_details(item=None, barcode=None):
	out = {}
	if barcode:
		out["item"] = frappe.db.get_value(
			"Item Barcode", filters={"barcode": barcode}, fieldname=["parent"])
		if not out["item"]:
			frappe.throw(
				_("Invalid Barcode. There is no Item attached to this barcode."))
	else:
		out["item"] = item

	barcodes = frappe.db.get_values("Item Barcode", filters={"parent": out["item"]},
		fieldname=["barcode"])

	out["selling_price"] = get_item_rate(out["item"])
	# out["last_buying_rate"] = get_last_buying_rate(out["item"])

	out["barcodes"] = [x[0] for x in barcodes]
	out["image"] = frappe.db.get_value("Item",
		filters={"name": out["item"]}, fieldname=["image"])
	return out


def get_item_rate(item):
	price_list = "Standard Selling"
	item_rate = frappe.db.get_values("Item Price", filters={"item_code":item,"price_list":price_list,"selling":1},fieldname=["price_list_rate"])
	if item_rate:
		return item_rate[0][0]
	return 0
