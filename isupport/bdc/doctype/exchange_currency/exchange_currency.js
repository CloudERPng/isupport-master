// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exchange Currency', {
	onload: function(frm) {
		frm.trigger("make_btns");
		frm.trigger("render_transactions");
	},
	refresh: function(frm) {
		frm.trigger("make_btns");
		frm.trigger("render_transactions");
	},
	setup: function(frm) {
		frm.set_query("rec_account", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.company],
					["account_type","in", ["Bank","Cash"]],
					["account_currency","=", frm.doc.receive_currency],
					["is_group","=", 0],
				]
			};
		});
		frm.set_query("pay_account", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.company],
					["account_type","in", ["Bank","Cash"]],
					["account_currency","=", frm.doc.pay_currency],
					["is_group","=", 0],
				]
			};
		});
	},
	render_transactions: function(frm) {
		frm.call('get_transactions').then( r => {
			if(!r.exc) {
				$("#transactions").remove();
				const transactions = $(`<div class="modal-body ui-front" id="transactions">
						<h4>Exchange Currency Transactions :</h4>
						<table class="table table-bordered">
						<thead>
							<tr>
							<th>Date</th>
							<th>Account</th>
							<th>Currency</th>
							<th>Debit</th>
							<th>Credit</th>
							<th>Customer</th>
							<th>Bank Name</th>
							<th>Account Name</th>
							<th>Account IBN</th>
							<th>Type</th>
							</tr>
						</thead>
						<tbody>
						</tbody>
						</table>
					</div>`).appendTo(frm.fields_dict.transactions.wrapper);
					const tbody = $(transactions).find('tbody');
				r.message.forEach(element => {
					const tr = $(`
					<tr>
						<td>${element.date.slice(0,19)}</td>
						<td>${element.account}</td>
						<td>${element.account_currency}</td>
						<td>${element.debit.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') || ''}</td>
						<td>${element.credit.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') || ''}</td>
						<td>${element.exchange_customer || ''}</td>
						<td>${element.bank_name || ''}</td>
						<td>${element.bank_account_name || ''}</td>
						<td>${element.bank_account_iban || ''}</td>
						<td>${element.exchange_reference}</td>
					</tr>
					`).appendTo(tbody);
				});
			frm.refresh_field('transactions');
			}	
		});
		// some function here after this run
	},
	receive_currency: function(frm) {
		frm.trigger("get_exchange_rate");
		frappe.call({
			method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_profile_account',
			args: {
				profile: frm.doc.profile,
				currency: frm.doc.receive_currency,
			},
			callback: (r) => {
				if(r.message) {
					frm.set_value("rec_account",r.message);
				}
			},
		})
	},
	pay_currency: function(frm) {
		frm.trigger("get_exchange_rate");
		frm.trigger("set_amount");
		frm.trigger("get_exchange_rate");
		frappe.call({
			method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_profile_account',
			args: {
				profile: frm.doc.profile,
				currency: frm.doc.pay_currency,
			},
			callback: (r) => {
				if(r.message) {
					frm.set_value("pay_account",r.message);
				}
			},
		})
	},
	get_exchange_rate: function(frm) {
		frappe.call({
			method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_rate',
			args: {
				to_currency: frm.doc.pay_currency,
				from_currency: frm.doc.receive_currency,
				company: frm.doc.company,
			},
			async: false,
			callback: (r) => {
				if(!r.exc) {
					frm.set_value("exchange_rate",r.message);
					frm.set_value("py_amount",frm.doc.rec_amount * r.message);
				}
			},
			error: (r) => {
				// on error
			}
		})
	},
	broker_exchange_rate: function(frm) {
		if (frm.doc.based_on_exchange_rate != 1) {return;}
		var broker_currency_exchange_rate = 1;
		frappe.call({
			method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_rate',
			args: {
				to_currency: frm.doc.commission_currency,
				from_currency: frm.doc.pay_currency,
				company: frm.doc.company,
			},
			async: false,
			callback: (r) => {
				if(!r.exc) {
					broker_currency_exchange_rate = r.message;
				}
			},
			error: (r) => {
				// on error
			}
		});
		var commission_amount = flt((frm.doc.exchange_rate - frm.doc.broker_exchange_rate) * frm.doc.rec_amount * broker_currency_exchange_rate, 3);
		if (commission_amount < 0) {commission_amount = 0}
		frm.set_value("commission_amount",commission_amount);
	},
	commission_currency: function(frm) {
		frm.trigger("broker_exchange_rate");
	},
	set_broker_amount: function(frm) {
		if (frm.doc.based_on_exchange_rate != 1) {
			frm.set_value("broker_exchange_rate",0);
		}
		else {
			frm.set_value("broker_exchange_rate",frm.doc.exchange_rate);
			frm.trigger("broker_exchange_rate");
		}
	},
	based_on_exchange_rate: function(frm) {
		frm.trigger("set_broker_amount");
	},
	rec_amount: function(frm) {
		frm.trigger("get_exchange_rate");
		frm.trigger("set_amount");
		frm.trigger("set_broker_amount");
	},
	type: function(frm) {
		frm.trigger("get_exchange_rate");
		frm.trigger("set_amount");
	},
	exchange_rate: function(frm) {
		frm.trigger("set_amount");
		if (frm.doc.exchange_rate != 0) {
			frm.doc.rev_exchange_rate = 1/frm.doc.exchange_rate;
		}
		else {
			frm.doc.rev_exchange_rate  = 0;
		}
		frm.refresh_field('rev_exchange_rate');
		frm.trigger("set_broker_amount");
	},
	rev_exchange_rate: function(frm) {
		frm.doc.exchange_rate = 1/frm.doc.rev_exchange_rate;
		frm.refresh_field('exchange_rate');
		frm.trigger("set_amount");
		frm.trigger("set_broker_amount");
	},
	set_amount: function(frm) {
		frm.set_value("py_amount",frm.doc.rec_amount * frm.doc.exchange_rate);
	},
	commission : function(frm) {
		if(frm.doc.commission == 1) {
			frm.set_value("broker",frm.doc.customer);
		}
	},
	broker : function(frm) {
		frappe.db.get_value('Customer', {name: frm.doc.broker}, 'default_currency', (r) => {
			if(r.default_currency) {
				frm.set_value("commission_currency",r.default_currency);
			}
			else {
				frm.set_value("commission_currency",frm.doc.company_currency);
			}
		});
	},
	make_btns: function(frm){
		if (frm.doc.docstatus == 1 && flt(frm.doc.rec_amount,precision("rec_amount")) - flt(frm.doc.total_recived,precision("total_recived")) > 0){
			cur_frm.add_custom_button(__("Add Incoming Payment"), function() {
				var default_account = "" ;
				frappe.call({
					method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_profile_account',
					args: {
						profile: frm.doc.profile,
						currency: frm.doc.receive_currency,
					},
					async: false,
					callback: (r) => {
						if(r.message) {
							default_account = r.message;
						}
					},
				}) ;
				let d = new frappe.ui.Dialog({
					title: 'Add Incoming Payment',
					fields: [
						{
							label: 'Incoming Payment',
							fieldname: 'payment',
							fieldtype: 'Float',
							default: frm.doc.rec_amount - frm.doc.total_recived,
							reqd: 1,
						},
						{
							label: 'Currency',
							fieldname: 'Currency',
							fieldtype: 'Read Only',
							default: frm.doc.receive_currency,
						},
						{
							label: 'Account',
							fieldname: 'account',
							fieldtype: 'Link',
							options: 'Account',
							default: default_account,
							reqd: 1,
							filters: {
								company: frm.doc.company,
								account_currency: frm.doc.receive_currency,
								is_group: 0,
								account_type: ["in", ["Bank","Cash"]]
							},
						},
						{
							label: 'Bank Name',
							fieldname: 'bank_name',
							fieldtype: 'Link',
							options: 'Bank',
							default: frm.doc.in_bank_name,
						},
						{
							label: 'Bank Account Name',
							fieldname: 'bank_account_name',
							fieldtype: 'Data',
							default: frm.doc.in_bank_account_name,
						},
						{
							label: 'Bank Account IBAN',
							fieldname: 'bank_account_iban',
							fieldtype: 'Data',
							default: frm.doc.in_bank_account_iban,
						},
					],
					primary_action_label: 'Submit',
					primary_action(values) {
						frappe.call({
							method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.make_entry',
							args: {
								exchange_currency_name: frm.doc.name,
								amount: values.payment,
								account: values.account,
								entry_type: 'in',
								bank_name: values.bank_name,
								bank_account_name: values.bank_account_name,
								bank_account_iban: values.bank_account_iban,
							},
							async: false,
							callback: (r) => {
								if(r.message) {
									frm.reload_doc();
								}
							},
						}) ;
						d.hide();
					}
				});
				d.show();
			});
		}
		if (frm.doc.docstatus == 1 && flt(frm.doc.py_amount,precision("py_amount")) - flt(frm.doc.total_payed,precision("total_payed"))){
			cur_frm.add_custom_button(__("Add Outgoing Payment"), function() {
				var default_account = "" ;
				frappe.call({
					method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_profile_account',
					args: {
						profile: frm.doc.profile,
						currency: frm.doc.pay_currency,
					},
					async: false,
					callback: (r) => {
						if(r.message) {
							default_account = r.message;
						}
					},
				}) ;
				let d = new frappe.ui.Dialog({
					title: 'Add Outgoing Payment',
					fields: [
						{
							label: 'Outgoing Payment',
							fieldname: 'payment',
							fieldtype: 'Float',
							default: frm.doc.py_amount - frm.doc.total_payed,
							reqd: 1,
						},
						{
							label: 'Currency',
							fieldname: 'Currency',
							fieldtype: 'Read Only',
							default: frm.doc.pay_currency,
						},
						{
							label: 'Account',
							fieldname: 'account',
							fieldtype: 'Link',
							options: 'Account',
							default: default_account,
							reqd: 1,
							filters: {
								company: frm.doc.company,
								account_currency: frm.doc.pay_currency,
								is_group: 0,
								account_type: ["in", ["Bank","Cash"]]
							},
						},
						{
							label: 'Bank Name',
							fieldname: 'bank_name',
							fieldtype: 'Link',
							options: 'Bank',
							default: frm.doc.out_bank_name,
						},
						{
							label: 'Bank Account Name',
							fieldname: 'bank_account_name',
							fieldtype: 'Data',
							default: frm.doc.out_bank_account_name,
						},
						{
							label: 'Bank Account IBAN',
							fieldname: 'bank_account_iban',
							fieldtype: 'Data',
							default: frm.doc.out_bank_account_iban,
						},
					],
					primary_action_label: 'Submit',
					primary_action(values) {
						frappe.call({
							method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.make_entry',
							args: {
								exchange_currency_name: frm.doc.name,
								amount: values.payment,
								account: values.account,
								entry_type: 'out',
								bank_name: values.bank_name,
								bank_account_name: values.bank_account_name,
								bank_account_iban: values.bank_account_iban,
							},
							async: false,
							callback: (r) => {
								if(r.message) {
									frm.reload_doc();
								}
							},
						}) ;
						d.hide();
					}
				});
				
				d.show();
			});
		}
		if (frm.doc.docstatus == 1 && ["Completed","Commission"].includes(frm.doc.status) && frm.doc.commission == 1 && frm.doc.commission_amount > frm.doc.total_commission){
			cur_frm.add_custom_button(__("Add Commission Payment"), function() {
				var default_account = "" ;
				frappe.call({
					method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.get_broker_cash_account',
					args: {
						broker: frm.doc.broker,
					},
					async: false,
					callback: (r) => {
						if(r.message) {
							default_account = r.message;
						}
					},
				}) ;
				let d = new frappe.ui.Dialog({
					title: 'Add Commission Payment',
					fields: [
						{
							label: 'Commission Payment',
							fieldname: 'payment',
							fieldtype: 'Read Only',
							default: frm.doc.commission_amount,
						},
						{
							label: 'Currency',
							fieldname: 'Currency',
							fieldtype: 'Read Only',
							default: frm.doc.commission_currency,
						},
						{
							label: 'Account',
							fieldname: 'account',
							fieldtype: 'Link',
							options: 'Account',
							default: default_account,
							reqd: 1,
							filters: {
								company: frm.doc.company,
								account_currency: frm.doc.commission_currency,
								is_group: 0,
								account_type: ["in", ["Bank","Cash"]]
							},
						},
						{
							label: 'Bank Name',
							fieldname: 'bank_name',
							fieldtype: 'Link',
							options: 'Bank',
							default: frm.doc.broker_bank_name,
						},
						{
							label: 'Bank Account Name',
							fieldname: 'bank_account_name',
							fieldtype: 'Data',
							default: frm.doc.broker_bank_account_name,
						},
						{
							label: 'Bank Account IBAN',
							fieldname: 'bank_account_iban',
							fieldtype: 'Data',
							default: frm.doc.broker_bank_account_iban,
						},
					],
					primary_action_label: 'Submit',
					primary_action(values) {
						frappe.call({
							method: 'isupport.bdc.doctype.exchange_currency.exchange_currency.make_commission_entry',
							args: {
								exchange_currency_name: frm.doc.name,
								amount: values.payment,
								account: values.account,
								bank_name: values.bank_name,
								bank_account_name: values.bank_account_name,
								bank_account_iban: values.bank_account_iban,
							},
							async: false,
							callback: (r) => {
								if(r.message) {
									frm.reload_doc();
								}
							},
						}) ;
						d.hide();
					}
				});
				
				d.show();
			});
		}
	},
});
