# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import flt
import frappe
from frappe import _


def set_default_markup_margin(doc, method):
    if doc.is_new():
        doc.sales_margin, doc.sales_markup = frappe.get_value("Item Group",doc.item_group,["sales_margin","sales_markup"])