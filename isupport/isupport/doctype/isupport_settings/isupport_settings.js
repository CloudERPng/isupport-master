// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('ISupport Settings', {
	refresh: function(frm) {
		if (frappe.user_roles.includes("Administrator")) {
			console.log("Super Special access granted to " + frappe.session.user)
			frm.set_df_property("support_url", "read_only", false);
			frm.set_df_property("support_email", "read_only", false);
			
		} else {
			frm.set_df_property("support_url", "read_only", true);
			frm.set_df_property("support_email", "read_only", true);

		}
	}
});
