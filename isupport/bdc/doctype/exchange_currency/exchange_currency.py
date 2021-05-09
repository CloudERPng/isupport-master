# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
# from erpnext.setup.utils import get_exchange_rate
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, add_days
from frappe import _
from erpnext.accounts.party import get_party_account
from isupport.tools import print_out

class ExchangeCurrency(Document):
	
	def onload(self):
		make_exchange_close_entry(self.name)
		self.get_transactions()

	def before_insert(self):
		self.status = "Draft"


	def on_submit(self):
		self.make_gl_entries()
		if self.commission != 1:
			self.status = "Unpaid" if self.is_contract == 1 else "Completed"
		else:
			self.status = "Unpaid" if self.is_contract == 1 else "Commission"
		self.db_set("status", self.status)

	def on_cancel(self):
		self.status = "Cancelled"
		self.db_set("status", "Cancelled")
	
	def validate(self):
		if self.receive_currency == self.pay_currency:
			frappe.throw(_("Please choose two different currencies"))
		if self.commission == 1 and self.commission_amount <= 0:
			frappe.throw(_("The commission amount cannot be less than or equal to zero"))

	def make_gl_entries(self):
		if self.is_contract == 1:
			return

		make_entry(self.name, flt(self.rec_amount,self.precision("rec_amount")), self.rec_account, "in")
		make_entry(self.name, flt(self.py_amount,self.precision("py_amount")), self.pay_account, "out")
		

	@frappe.whitelist()
	def get_transactions(self):
		query = """ SELECT 
						creation AS date, 
						account, 
						account_currency, 
						debit_in_account_currency AS debit,
						credit_in_account_currency AS credit, 
						exchange_customer, 
						bank_name, 
						bank_account_name,
						bank_account_iban, 
						exchange_reference
				FROM `tabJournal Entry Account` 
				WHERE 
					reference_name = '%s'
					AND docstatus= 1 
					AND (exchange_reference = 'Broker Cash' OR exchange_reference = 'Cash')
					ORDER BY creation
				""" %(self.name)
		data = frappe.db.sql(query,as_dict=True)
		return data


@frappe.whitelist()
def get_rate(from_currency, to_currency, company, args=None):
	args = ""
	rate = 0
	rate = get_exchange_rate(from_currency, to_currency, now_datetime(), args)
	if rate == 0:
		frappe.log_error(title="Get Exchange Rate")
		frappe.msgprint(_("Unable to find exchange rate for {0} to {1} for key date {2}. Please create a Currency Exchange record manually").format(from_currency, to_currency, now_datetime()))
		rev_rate =  get_exchange_rate(to_currency, from_currency, now_datetime(), args)
		if rev_rate == 0:
			frappe.log_error(title="Get Exchange Rate")
			frappe.msgprint(_("Unable to find exchange rate for {0} to {1} for key date {2}. Please create a Currency Exchange record manually").format(from_currency, to_currency, now_datetime()))
			return 0
		else:
			rate = 1 / rev_rate
	return rate


@frappe.whitelist()
def get_profile_account(profile, currency):
	account = frappe.get_all(
            "Currency Account",
            filters = [
                ["Currency Account","parent","=",profile],
                ["Currency Account","currency","=",currency]
            ],
            fields = ["account"]
        )
	return account[0]["account"] if len(account) > 0 else ""



def get_rec_amount(exchange_currency_name, account_currency):
	query = """ SELECT SUM(debit_in_account_currency) as sum_amount 
			FROM `tabJournal Entry Account` 
			WHERE 
				reference_name = '%s'
				AND account_currency = '%s'
				AND (party IS NULL OR party = '')
				AND (account_type = "Cash" OR account_type = "Bank")
				AND docstatus= 1 
				AND exchange_reference = 'Cash'
			
			""" %(exchange_currency_name,account_currency)

	return frappe.db.sql(query,as_dict=True)[0]["sum_amount"]


def get_pay_amount(exchange_currency_name, account_currency):
	query = """ SELECT SUM(credit_in_account_currency) as sum_amount 
			FROM `tabJournal Entry Account` 
			WHERE 
				reference_name = '%s'
				AND account_currency = '%s'
				AND (party IS NULL OR party = '')
				AND (account_type = "Cash" OR account_type = "Bank")
				AND docstatus= 1 
				AND exchange_reference = 'Cash'
			
			""" %(exchange_currency_name,account_currency)

	return  frappe.db.sql(query,as_dict=True)[0]["sum_amount"]


@frappe.whitelist()
def make_entry(exchange_currency_name, amount, account, entry_type, bank_name=None, bank_account_name=None, bank_account_iban=None):
	doc = frappe.get_doc("Exchange Currency",exchange_currency_name)
	account_pay_currency = account
	account_receive_currency = account
	default_currency = doc.company_currency
	party_account = get_party_account("Customer", doc.customer, doc.company)
	party_currency = frappe.get_value("Account", party_account, "account_currency")
	party_rate = get_rate(party_currency, default_currency, doc.company)
	pay_rate = get_rate(doc.pay_currency, default_currency, doc.company)
	receive_rate = get_rate(doc.receive_currency, default_currency, doc.company)
	exchange_gain_loss_account = frappe.get_cached_value('Company', doc.company, "exchange_gain_loss_account")
	cash_tag = "Cash"
	customer_tag = "Customer"
	# broker_tag = "Broker"
	diff_tag = "Diff"
	
	if entry_type == "in":
		jl_rows = []
		debit_row = dict(
			account = account_receive_currency,
			debit_in_account_currency = flt(amount,doc.precision("rec_amount")),
			account_curremcy = doc.receive_currency,
			exchange_rate = 1 if doc.receive_currency == default_currency else flt(receive_rate),
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = cash_tag,
			exchange_customer = doc.exchange_customer or "",
			bank_name = bank_name or doc.in_bank_name or "",
			bank_account_name = bank_account_name or doc.in_bank_account_name or "",
			bank_account_iban = bank_account_iban or doc.in_bank_account_iban or "",
		)
		jl_rows.append(debit_row)

		credit_in_account_currency = flt(flt(amount,doc.precision("rec_amount")) * flt(receive_rate) / flt(party_rate),doc.precision("rec_amount"))
		credit_row_1 = dict(
			party_type = "customer",
			party = doc.customer,
			account = party_account,
			credit_in_account_currency = credit_in_account_currency,
			account_curremcy = party_currency,
			exchange_rate = 1 if party_currency == default_currency else flt(party_rate),
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = customer_tag
		)
		jl_rows.append(credit_row_1)

		diff_value = (flt(amount) * flt(receive_rate)) - (credit_in_account_currency * flt(party_rate))
		if diff_value != 0:
			ballance_row = dict(
			account = exchange_gain_loss_account,
			debit_in_account_currency = (diff_value * (-1)) if diff_value < 0 else 0,
			credit_in_account_currency = diff_value if diff_value > 0 else 0,
			account_curremcy = default_currency,
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = diff_tag
			)
			jl_rows.append(ballance_row)
		
		user_remark = "Against Exchange Currency " + doc.name + " For Customer " + doc.customer + " " + str(doc.rec_amount)+ " " + doc.receive_currency
		jv_doc = frappe.get_doc(dict(
			doctype = "Journal Entry",
			posting_date = doc.date,
			accounts = jl_rows,
			company = doc.company,
			multi_currency = 1,
			user_remark = user_remark,
		))

		jv_doc.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		jv_doc.save()
		jv_doc.submit()
		jv_url = frappe.utils.get_url_to_form(jv_doc.doctype, jv_doc.name)
		si_msgprint = "Journal Entry Created <a href='{0}'>{1}</a>".format(jv_url,jv_doc.name)
		frappe.msgprint(_(si_msgprint))
		return jv_doc.name

	if entry_type == "out":
		jl_rows = []
		debit_in_account_currency = flt(flt(amount,doc.precision("py_amount")) * flt(pay_rate) / flt(party_rate),doc.precision("py_amount"))
		debit_row_1 = dict(
			party_type = "customer",
			party = doc.customer,
			account = party_account,
			debit_in_account_currency = debit_in_account_currency,
			account_curremcy = party_currency,
			exchange_rate = 1 if party_currency == default_currency else flt(party_rate),
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = customer_tag
		)
		jl_rows.append(debit_row_1)

		credit_row = dict(
			account = account_pay_currency,
			credit_in_account_currency = flt(amount,doc.precision("py_amount")),
			account_curremcy = doc.pay_currency,
			exchange_rate = 1 if doc.pay_currency == default_currency else flt(pay_rate),
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = cash_tag,
			exchange_customer = doc.exchange_customer or "",
			bank_name = bank_name or doc.out_bank_name or "",
			bank_account_name = bank_account_name or doc.out_bank_account_name or "",
			bank_account_iban = bank_account_iban or doc.out_bank_account_iban or "",
		)
		jl_rows.append(credit_row)

		diff_value = (debit_in_account_currency * flt(party_rate)) - (flt(amount) * flt(pay_rate))
		if diff_value != 0:
			ballance_row = dict(
			account = exchange_gain_loss_account,
			debit_in_account_currency = (diff_value * (-1)) if diff_value < 0 else 0,
			credit_in_account_currency = diff_value if diff_value > 0 else 0,
			account_curremcy = default_currency,
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = diff_tag
			)
			jl_rows.append(ballance_row)

		user_remark = "Against Exchange Currency " + doc.name + " For Customer " + doc.customer + " " + str(doc.rec_amount)+ " " + doc.receive_currency
		jv_doc = frappe.get_doc(dict(
			doctype = "Journal Entry",
			posting_date = doc.date,
			accounts = jl_rows,
			company = doc.company,
			multi_currency = 1,
			user_remark = user_remark
		))

		jv_doc.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		jv_doc.save()
		jv_doc.submit()
		jv_url = frappe.utils.get_url_to_form(jv_doc.doctype, jv_doc.name)
		si_msgprint = "Journal Entry Created <a href='{0}'>{1}</a>".format(jv_url,jv_doc.name)
		frappe.msgprint(_(si_msgprint))
		return jv_doc.name


def update_totals(doc,method):
	float_precision = cint(frappe.db.get_default("float_precision")) or 3
	for i in doc.accounts:
		if i.reference_type == "Exchange Currency":
			if not i.party and i.debit_in_account_currency:
				if i.account_currency == frappe.get_value("Exchange Currency", i.reference_name, "receive_currency"):
					rec_total = get_rec_amount(i.reference_name, i.account_currency) or 0
					rec_amount = frappe.get_value("Exchange Currency", i.reference_name, "rec_amount")
					if flt(rec_total,float_precision) > flt(rec_amount,float_precision):
						frappe.throw(_("The amount should not be greater than ") + str(flt(rec_amount, float_precision) - flt(frappe.get_value("Exchange Currency", i.reference_name, "total_recived"),float_precision)))
					frappe.db.set_value('Exchange Currency', i.reference_name, 'total_recived', rec_total)
					frappe.db.commit()
					update_status(i.reference_name)
				

			if not i.party and i.credit_in_account_currency:
				if i.account_currency == frappe.get_value("Exchange Currency", i.reference_name, "pay_currency"):
					pay_total = get_pay_amount(i.reference_name, i.account_currency) or 0
					pay_amount = frappe.get_value("Exchange Currency", i.reference_name, "py_amount")
					if flt(pay_total,float_precision) > flt(pay_amount,float_precision):
						frappe.throw(_("The amount should not be greater than ") + str(flt(pay_amount) - flt(frappe.get_value("Exchange Currency", i.reference_name, "total_payed"),float_precision)))
					frappe.db.set_value('Exchange Currency', i.reference_name, 'total_payed', pay_total)
					frappe.db.commit()
					update_status(i.reference_name)
			
			if i.exchange_reference == "Broker Cash":
				total = get_total_commission(i.reference_name, i.account, i.account_currency) or 0
				frappe.db.set_value('Exchange Currency', i.reference_name, 'total_commission', total)
				frappe.db.commit()
				update_status(i.reference_name)


def update_status(exchange_currency_name):
	float_precision = cint(frappe.db.get_default("float_precision")) or 3
	doc = frappe.get_doc("Exchange Currency",exchange_currency_name)
	diff_rec = flt(doc.rec_amount,float_precision) - flt(doc.total_recived,float_precision)
	diff_pay = flt(doc.py_amount,float_precision) - flt(doc.total_payed,float_precision)
	# com_rate = get_rate(doc.commission_currency, doc.company_currency, doc.company)
	diff_com = flt(doc.commission_amount, float_precision) - flt(doc.total_commission, float_precision)
	status = ""
		
	if diff_rec == 0 and diff_pay == 0:
		if doc.commission == 1 and diff_com == 0: 
			status =  "Completed"
		elif doc.commission == 1 and diff_com > 0: 
			status =  "Commission"
		elif doc.commission != 1:
			status =  "Completed"
	elif diff_rec == 0:
		status =  "Incoming Completed"
	elif diff_pay == 0:
		status =  "Outgoing Completed"
	else :
		status =  "Unpaid"
	
	if status:
		frappe.db.set_value('Exchange Currency', doc.name, 'status', status)


@frappe.whitelist()
def make_commission_entry(exchange_currency_name, amount, account, bank_name=None, bank_account_name=None, bank_account_iban=None):
	doc = frappe.get_doc("Exchange Currency",exchange_currency_name)
	float_precision = cint(frappe.db.get_default("float_precision")) or 3
	amount = flt(amount,float_precision)
	broker_account = get_party_account("Customer", doc.broker, doc.company)
	exchange_gain_loss_account = frappe.get_cached_value('Company', doc.company, "exchange_gain_loss_account")
	broker_tag = "Broker"
	broker_expenses_tag = "Broker Expenses"
	broker_cash_tag = "Broker Cash"
	if doc.commission:
		if not doc.broker or not doc.commission_currency or not doc.commission_amount:
			frappe.throw(_("Please fill in all fields of Commission Section"))
		
		default_currency = doc.company_currency
		commission_rate = get_rate(doc.commission_currency, default_currency, doc.company)
		jl_rows = []

		debit_broker_row = dict(
			account = exchange_gain_loss_account,
			debit_in_account_currency = commission_rate * flt(amount),
			account_curremcy = default_currency,
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = broker_expenses_tag
		)
		jl_rows.append(debit_broker_row)

		credit_row = dict(
			party_type = "customer",
			party = doc.broker,
			account = broker_account,
			credit_in_account_currency = commission_rate * flt(amount),
			exchange_rate = 1 if doc.commission_currency == default_currency else flt(commission_rate),
			account_curremcy = doc.commission_currency,
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = broker_tag
		)
		jl_rows.append(credit_row)

		debit_row = dict(
			party_type = "customer",
			party = doc.broker,
			account = broker_account,
			debit_in_account_currency = commission_rate * flt(amount),
			account_curremcy = commission_rate * flt(amount),
			exchange_rate = 1 if doc.commission_currency == default_currency else flt(commission_rate),
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = broker_tag
		)
		jl_rows.append(debit_row)

		credit_broker_row = dict(
			account = account,
			credit_in_account_currency = amount,
			exchange_rate = 1 if doc.commission_currency == default_currency else flt(commission_rate),
			account_curremcy = doc.commission_currency,
			cost_center =  doc.cost_center,
			reference_type = "Exchange Currency",
			reference_name = doc.name,
			exchange_reference = broker_cash_tag,
			bank_name = bank_name or doc.broker_bank_name or "",
			bank_account_name = bank_account_name or doc.broker_bank_account_name or "",
			bank_account_iban = bank_account_iban or doc.broker_bank_account_iban or "",
		)
		jl_rows.append(credit_broker_row)

		user_remark = "Against Exchange Currency " + doc.name + " For Customer " + doc.customer + " " + str(doc.rec_amount)+ " " + doc.receive_currency
		jv_doc = frappe.get_doc(dict(
			doctype = "Journal Entry",
			posting_date = doc.date,
			accounts = jl_rows,
			company = doc.company,
			multi_currency = 1,
			user_remark = user_remark
		))

		jv_doc.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		jv_doc.save()
		jv_doc.submit()
		jv_url = frappe.utils.get_url_to_form(jv_doc.doctype, jv_doc.name)
		si_msgprint = "Journal Entry Created <a href='{0}'>{1}</a>".format(jv_url,jv_doc.name)
		frappe.msgprint(_(si_msgprint))
		return jv_doc.name


@frappe.whitelist()
def get_broker_cash_account(broker):
	# return frappe.get_value("Broker",broker, "bank_account")
	return ""


def get_total_commission(exchange_currency_name, account_name, account_currency):
	query = """ SELECT SUM(credit_in_account_currency) as sum_amount 
			FROM `tabJournal Entry Account` 
			WHERE 
				reference_name = '%s'
				AND account = '%s'
				AND account_currency = '%s'
				AND docstatus= 1 
				AND exchange_reference = 'Broker Cash'
			
			""" %(exchange_currency_name,account_name,account_currency)

	return frappe.db.sql(query,as_dict=True)[0]["sum_amount"]


def get_diff_exchange(exchange_currency_name,customer):
	query = """ SELECT SUM(debit_in_account_currency) as sum_debit ,SUM(credit_in_account_currency) as sum_credit
			FROM `tabJournal Entry Account` 
			WHERE 
				reference_name = '%s'
				AND party = '%s'
				AND docstatus= 1 
			
			""" %(exchange_currency_name,customer)
	totals = frappe.db.sql(query,as_dict=True)
	if len(totals) > 0 : 
		if not totals[0]["sum_credit"]:
			totals[0]["sum_credit"] = 0
		if not totals[0]["sum_debit"]:
			totals[0]["sum_debit"] = 0
		return totals[0]["sum_credit"] - totals[0]["sum_debit"]
	else :
		return 0


def make_exchange_close_entry(exchange_currency_name):
	doc = frappe.get_doc("Exchange Currency",exchange_currency_name)
	if doc.status != "Completed" or doc.docstatus != 1:
		return
	diff_value = get_diff_exchange(exchange_currency_name,doc.customer)
	if diff_value == 0:
		return
	default_currency = doc.company_currency
	party_account = get_party_account("Customer", doc.customer, doc.company)
	party_currency = frappe.get_value("Account", party_account, "account_currency")
	party_rate = get_rate(party_currency, default_currency, doc.company)
	exchange_gain_loss_account = frappe.get_cached_value('Company', doc.company, "exchange_gain_loss_account")
	customer_tag = "Customer"
	diff_tag = "Diff"

	jl_rows = []
	amount = diff_value * party_rate

	ballance_row = dict(
		account = exchange_gain_loss_account,
		debit_in_account_currency = (amount * (-1)) if diff_value < 0 else 0,
		credit_in_account_currency = amount if diff_value > 0 else 0,
		account_curremcy = default_currency,
		cost_center =  doc.cost_center,
		reference_type = "Exchange Currency",
		reference_name = doc.name,
		exchange_reference = diff_tag
	)
	jl_rows.append(ballance_row)

	customer_row = dict(
		party_type = "customer",
		party = doc.customer,
		account = party_account,
		debit_in_account_currency = diff_value if diff_value > 0 else 0,
		credit_in_account_currency = (diff_value * (-1)) if diff_value < 0 else 0,
		account_curremcy = party_currency,
		exchange_rate = 1 if party_currency == default_currency else flt(party_rate),
		cost_center =  doc.cost_center,
		reference_type = "Exchange Currency",
		reference_name = doc.name,
		exchange_reference = customer_tag
		)
	jl_rows.append(customer_row)
	
	user_remark = "Against Exchange Currency " + doc.name + " For Customer " + doc.customer + " " + str(doc.rec_amount)+ " " + doc.receive_currency
	jv_doc = frappe.get_doc(dict(
		doctype = "Journal Entry",
		posting_date = doc.date,
		accounts = jl_rows,
		company = doc.company,
		multi_currency = 1,
		user_remark = user_remark,
		reference_type = "Exchange Currency",
		reference_name = doc.name
	))

	jv_doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	jv_doc.save()
	jv_doc.submit()
	frappe.db.commit()
	jv_url = frappe.utils.get_url_to_form(jv_doc.doctype, jv_doc.name)
	si_msgprint = "Journal Entry Created <a href='{0}'>{1}</a>".format(jv_url,jv_doc.name)
	frappe.msgprint(_(si_msgprint))
	return jv_doc.name


def get_exchange_rate(from_currency, to_currency, transaction_date=None, args=None):
	if not (from_currency and to_currency):
		# manqala 19/09/2016: Should this be an empty return or should it throw and exception?
		return
	if from_currency == to_currency:
		return 1

	if not transaction_date:
		transaction_date = nowdate()
	currency_settings = frappe.get_doc("Accounts Settings").as_dict()
	allow_stale_rates = currency_settings.get("allow_stale")

	filters = [
		["date", "<=", get_datetime_str(transaction_date)],
		["from_currency", "=", from_currency],
		["to_currency", "=", to_currency]
	]

	if args == "for_buying":
		filters.append(["for_buying", "=", "1"])
	elif args == "for_selling":
		filters.append(["for_selling", "=", "1"])

	if not allow_stale_rates:
		stale_days = currency_settings.get("stale_days")
		checkpoint_date = add_days(transaction_date, -stale_days)
		filters.append(["date", ">", get_datetime_str(checkpoint_date)])

	# cksgb 19/09/2016: get last entry in Currency Exchange with from_currency and to_currency.
	entries = frappe.get_all(
		"Currency Exchange", fields=["exchange_rate"], filters=filters, order_by="date desc",
		limit=1)
	if entries:
		return flt(entries[0].exchange_rate)

	try:
		cache = frappe.cache()
		key = "currency_exchange_rate_{0}:{1}:{2}".format(transaction_date,from_currency, to_currency)
		value = cache.get(key)

		if not value:
			import requests
			api_url = "https://frankfurter.app/{0}".format(transaction_date)
			response = requests.get(api_url, params={
				"base": from_currency,
				"symbols": to_currency
			})
			# expire in 6 hours
			response.raise_for_status()
			value = response.json()["rates"][to_currency]

			cache.set_value(key, value, expires_in_sec=6 * 60 * 60)
		return flt(value)
	except:
		# frappe.log_error(title="Get Exchange Rate")
		# frappe.msgprint(_("Unable to find exchange rate for {0} to {1} for key date {2}. Please create a Currency Exchange record manually").format(from_currency, to_currency, transaction_date))
		return 0.0
	


