// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('UType', {
	refresh: function(frm) {
		if (frappe.user_roles.includes("Administrator")) {
			console.log("Super Special access granted to " + frappe.session.user)
			frm.set_df_property("type", "read_only", false);
			frm.set_df_property("enable", "read_only", false);
			frm.set_df_property("allowed", "read_only", false);
			frm.set_df_property("enable_all_roles", "read_only", false);
			frm.set_df_property("roles", "read_only", false);
			frm.set_df_property("enable_all_modules", "read_only", false);
			frm.set_df_property("modules", "read_only", false);
			frappe.meta.get_docfield("ModulesT", "module", frm.doc.name).read_only = 0;
			frappe.meta.get_docfield("ModulesT", "enable", frm.doc.name).read_only = 0;
		} else {
			frm.set_df_property("type", "read_only", true);
			frm.set_df_property("enable", "read_only", true);
			frm.set_df_property("allowed", "read_only", true);
			frm.set_df_property("enable_all_roles", "read_only", true);
			frm.set_df_property("roles", "read_only", true);
			frm.set_df_property("enable_all_modules", "read_only", true);
			frm.set_df_property("modules", "read_only", true);
			frappe.meta.get_docfield("ModulesT", "module", frm.doc.name).read_only = 1;
			frappe.meta.get_docfield("ModulesT", "enable", frm.doc.name).read_only = 1;
		}
		frappe.call({
            "method": "isupport.limitations.doctype.utype.utype.get_modules",
            callback: function(r) {
                if(r.message && r.message.length) {
					frappe.meta.get_docfield("ModulesT", "module", frm.doc.name).options = r.message;
                }
            }
        });
	}
});


frappe.ui.form.on('RolesT', {
	// refresh: function(frm) {

	// }

});


cur_frm.set_query("role", "roles", function() {
	return{
		"filters": [
			["Role", "name", "!=", "Administrator"],
			["Role", "name", "!=", "All"],
			["Role", "name", "!=", "Guest"],
		]
	}
});