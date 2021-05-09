// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Support Issue', {
	validate: function(frm) {
		frm.set_df_property("section_break_18", "hidden", 0);
		if (frm.doc.owner_user != cur_frm.selected_doc["owner"]){
			frm.set_value("owner_user",cur_frm.selected_doc["owner"]);
		};
		
		if (frm.doc.edited_user != frappe.session.user){
			console.log(frappe.session.user_fullname);
			frm.set_value("edited_user",frappe.session.user);
			frm.set_value("edited_user_name",frappe.session.user_fullname);

		};

	},

	refresh: function(frm) {
		// if (cur_frm.doc.owner_user == frappe.user.name){
			// frm.set_df_property("status", "read_only", 0);
		// };
		$('.comment-input-wrapper').hide();
		$('.btn-new-email').hide();
		$('.delete-comment').hide();
		$('.edit-comment').hide();
		frm.trigger("css_last_message");
		frm.trigger("css_comment");
		frm.trigger("invoiced");
	},

	onload: function(frm) {
		if (frm.is_new()) {
			frm.set_df_property("section_break_18", "hidden", 1);
		};
		frm.trigger("css_last_message");
		frm.trigger("css_comment");
		frm.trigger("bill_approval");
		frm.trigger("invoiced");
	},
	send_issue: function(frm) {
		frm.save();
	},
	css_last_message: function(frm){
		const last_message_div = $(".control-value.like-disabled-input.for-description")[1];
		// last_message_div.style.color="blue";
		last_message_div.style.backgroundColor="#B9F6CA";
	},
	css_comment: function(frm){
		const commnets = $("span:contains('Guest')").closest('.timeline-item').find(".reply.timeline-content-show");
		commnets.css("background-color", "#B9F6CA");
	},
	status: function (frm) {
		frm.doc.closed_by_support = 0;
		frm.doc.reopen_by_support = 0;
	},
	bill_approval: function (frm) {
		if (frm.doc.bill_approval == "Approved") {
			frm.set_df_property("status", "read_only", 1);
			frm.set_df_property("issue_type", "read_only", 1);
			frm.set_df_property("bill_approval", "read_only", 1);
		}
		else {
			frm.set_df_property("status", "read_only", 0);
			frm.set_df_property("issue_type", "read_only", 0);
			frm.set_df_property("bill_approval", "read_only", 0);
		}
	},
	invoiced: function(frm) {
		if (frm.doc.invoiced) {
			frm.set_df_property("status", "read_only", 1);
			frm.set_df_property("subject", "read_only", 1);
			frm.set_df_property("priority", "read_only", 1);
		}
	},
	
});
