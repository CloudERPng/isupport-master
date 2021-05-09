# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "isupport"
app_title = "ISupport"
app_publisher = "Youssef Restom"
app_description = "Application to support Frappe & Erpnext customers and add features"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "youssef@totrox.com"
app_license = "MIT"

# Includes in <head>
# ------------------

fixtures = [
	{"doctype":"Custom Field", "filters": [["name", "in", (
		"User-type_of_user",
    "Sales Invoice-delivery_status",
    "Sales Invoice Item-delivery_status",
    "Item-sales_margin",
    "Item-sales_markup",
    "Purchase Invoice Item-section_break_48",
    "Purchase Invoice Item-current_sale_price",
    "Purchase Invoice Item-suggested_sale_price",
    "Purchase Invoice Item-column_break_51",
    "Purchase Invoice Item-update_selling_price",
    "Purchase Receipt Item-section_break_53",
    "Purchase Receipt Item-current_sale_price",
    "Purchase Receipt Item-suggested_sale_price",
    "Purchase Receipt Item-column_break_56",
    "Purchase Receipt Item-update_selling_price",
    "Item Group-sales_markup",
    "Item Group-sales_margin",
    "Item Price-previous_rate",
    "Company-exchange_profile",
    "Journal Entry Account-exchange_reference",
    "Journal Entry Account-exchange_section",
    "Journal Entry Account-exchange_customer",
    "Journal Entry Account-bank_name",
    "Journal Entry Account-bank_account_name",
    "Journal Entry Account-bank_account_iban",
    "Journal Entry Account-column_break_33",
	)]]},
    {"doctype":"Property Setter", "filters": [["name", "in", (
        "Exchange Currency-exchange_rate-precision",
        "Journal Entry Account-reference_type-options",
	)]]},
  # {"doctype":"Desk Page", "filters": [["name", "in", (
  #       "BDC","ISupport",
	# )]]},

]

# include js, css files in header of desk.html
# app_include_css = "/assets/isupport/css/isupport.css"
# app_include_js = "/assets/isupport/js/isupport.js"
app_include_js = "/assets/js/menu.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/isupport/css/isupport.css"
# web_include_js = "/assets/isupport/js/isupport.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}
page_js = {"permission-manager" : "public/js/permission_manager.js"}


doctype_js = {
        "User":"public/js/user.js",
        "Domain Settings":"public/js/domain_settings.js",
        "Sales Invoice":"public/js/sales_invoice.js",
        "Item":"public/js/item.js",
        "Purchase Invoice":"public/js/purchase_invoice.js",
        "Purchase Receipt":"public/js/purchase_receipt.js",
        "Item Group":"public/js/item_group.js",
        "Item Price":"public/js/item_price.js",
        }

doc_events = {
  'User': {
    'validate': [
      'isupport.limitations.doctype.site_limitations.site_limitations.user_limit',
      'isupport.limitations.doctype.site_limitations.site_limitations.user_type_limit'
    ],
    'on_update': [
      'isupport.limitations.doctype.site_limitations.site_limitations.user_limit',
      'isupport.limitations.doctype.site_limitations.site_limitations.user_type_limit'
    ]
  },
  'Company': {
    "validate":'isupport.limitations.doctype.site_limitations.site_limitations.company_limit'
  },
  '*': {
    'submit': 'isupport.limitations.doctype.site_limitations.site_limitations.space_limit'
  },
  'File': {
    'validate': 'isupport.limitations.doctype.site_limitations.site_limitations.space_limit'
  },
  'SMS Log': {
    'validate': 'isupport.limitations.doctype.site_limitations.site_limitations.sms_limit'
  },
  'Sales Invoice': {
    'validate': 'isupport.sales_invoice.check_validate_delivery_note',
    'on_submit': 'isupport.sales_invoice.check_submit_delivery_note',
    'on_cancel': 'isupport.sales_invoice.check_cancel_delivery_note',
  },
  'Delivery Note': {
    'on_submit': 'isupport.sales_invoice.update_delivery_on_sales_invoice',
    'on_cancel': 'isupport.sales_invoice.update_delivery_on_sales_invoice',
  },
  'Chat Message': {
    'after_insert': 'isupport.sync.send_caht',
  },
  'Item': {
    'validate': 'isupport.item.set_default_markup_margin',
  },
  'Journal Entry': {
    'on_submit': 'isupport.bdc.doctype.exchange_currency.exchange_currency.update_totals',
    'on_cancel': 'isupport.bdc.doctype.exchange_currency.exchange_currency.update_totals',
  },
}
# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "isupport.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "isupport.install.before_install"
# after_install = "isupport.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "isupport.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"isupport.tasks.all"
# 	],
	"daily": [
		"'isupport.limitations.doctype.site_limitations.site_limitations.check_end_paln"
	],
# 	"hourly": [
# 		"isupport.tasks.hourly"
# 	],
# 	"weekly": [
# 		"isupport.tasks.weekly"
# 	]
# 	"monthly": [
# 		"isupport.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "isupport.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "isupport.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "isupport.task.get_dashboard_data"
# }

