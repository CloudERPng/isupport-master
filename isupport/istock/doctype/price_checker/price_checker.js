// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Checker', {
	setup: (frm) => {

	},

	make_custom_stock_report_button: (frm) => {
		if (frm.doc.item) {
			frm.add_custom_button(__('Stock Balance Report'), () => {
				frappe.set_route('query-report', 'Stock Balance',
					{ 'item_code': frm.doc.item, 'warehouse': frm.doc.warehouse });
			});
		}
	},

	refresh: (frm) => {
		frm.disable_save();
		const scan = $("#scan");
		scan.css({"color": "#40739e"});
	},

	check_warehouse_and_date: (frm) => {
		frm.doc.item = '';
		frm.refresh();
	},

	warehouse: (frm) => {
		if (frm.doc.item || frm.doc.item_barcode) {
			frm.trigger('get_stock_and_item_details');
		}
	},

	date: (frm) => {
		if (frm.doc.item || frm.doc.item_barcode) {
			frm.trigger('get_stock_and_item_details');
		}
	},

	item: (frm) => {
		frappe.flags.last_updated_element = 'item';
		frm.trigger('get_stock_and_item_details');
	},

	item_barcode: (frm) => {
		frappe.flags.last_updated_element = 'item_barcode';
		frm.trigger('get_stock_and_item_details');
	},

	get_stock_and_item_details: (frm) => {


		if (frm.doc.item || frm.doc.item_barcode) {
			let filters = {
			};
			if (frappe.flags.last_updated_element === 'item') {
				filters = { ...filters, ...{ item: frm.doc.item }};
			}
			else {
				filters = { ...filters, ...{ barcode: frm.doc.item_barcode }};
			}
			frappe.call({
				method: 'isupport.istock.doctype.price_checker.price_checker.get_stock_item_details',
				args: filters,
				callback: (r) => {
					if (r.message) {
						let fields = ['item', 'image', 'selling_price'];
						if (!r.message['barcodes'].includes(frm.doc.item_barcode)) {
							frm.doc.item_barcode = '';
							frm.refresh();
						}
						fields.forEach(function (field) {
							frm.set_value(field, r.message[field]);
						});
						const selling_price = $(".control-value.like-disabled-input.bold");
						selling_price.css({"color": "#40739e", "font-size": "250%"});
						
						frm.doc.item_barcode ="";
						setTimeout(function(){
							window.location.reload(1);
						 }, 200000);
					}
				}
			});
		}
	}
});
