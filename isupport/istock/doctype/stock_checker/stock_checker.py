# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance, get_stock_value_on
from erpnext import get_company_currency, get_default_company


class StockChecker(Document):
	pass

@frappe.whitelist()
def get_stock_item_details(warehouse, date, item=None, barcode=None):
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
	out["last_buying_rate"] = get_last_buying_rate(out["item"])

	out["barcodes"] = [x[0] for x in barcodes]
	out["qty"] = get_stock_balance(out["item"], warehouse, date)
	out["value"] = get_stock_value_on(warehouse, date, out["item"])
	out["image"] = frappe.db.get_value("Item",
		filters={"name": out["item"]}, fieldname=["image"])
	return out


def get_item_rate(item):
	price_list = "Standard Selling"
	item_rate = frappe.db.get_values("Item Price", filters={"item_code":item,"price_list":price_list,"selling":1},fieldname=["price_list_rate"])
	if item_rate:
		return item_rate[0][0]
	return 0


def get_last_buying_rate(item_code,currency=None,supplier=None,company=None):
	if not company:
		company = get_default_company()
	if not currency:
		currency = get_company_currency(company)
	item_code = "'{0}'".format(item_code)
	currency = "'{0}'".format(currency)

	if supplier:
		conditions = " and SI.customer = '%s'" % supplier
	else:
		conditions = ""

	query = """ SELECT max(SI.posting_date) as MaxDate
            FROM `tabPurchase Invoice` AS SI 
            INNER JOIN `tabPurchase Invoice Item` AS SIT ON SIT.parent = SI.name
            WHERE 
                SIT.item_code = {0} 
                AND SI.docstatus= 1
                AND SI.currency = {2}
                AND SI.is_return != 1
                AND SI.company = '{3}'
                {1}""".format(item_code,conditions,currency,company)
			

	items_list = frappe.db.sql(query,as_dict=True)
	date = str(items_list[0]["MaxDate"])

	query2 = """ SELECT SI.name, SI.posting_date, SI.supplier, SIT.item_code, SIT.qty, SIT.rate
            FROM `tabPurchase Invoice` AS SI 
            INNER JOIN `tabPurchase Invoice Item` AS SIT ON SIT.parent = SI.name
            WHERE 
                SIT.item_code = {0} 
                AND SI.docstatus= 1
                AND SI.posting_date= '{4}'
                AND SI.currency = {2}
                AND SI.is_return != 1
                AND SI.company = '{3}'
                {1}""".format(item_code,conditions,currency,company,date)
			
	items_rate = frappe.db.sql(query2,as_dict=True)
	if items_rate and len(items_rate) > 0:
		return items_rate[0]["rate"]
	else: 
		return 0