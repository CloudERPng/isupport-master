// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exchange Profile', {
	setup: function(frm) {
		frm.set_query("cost_center", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.company],
				]
			};
		});
	
	frm.set_query("account","account", function() {
		return {
			"filters": [
				["company","=", frm.doc.company],
				["account_type","in", ["Bank","Cash"]],
				// ["account_currency","=", frm.doc.currency],
				["is_group","=", 0],
			]
		};
	});
},
});
