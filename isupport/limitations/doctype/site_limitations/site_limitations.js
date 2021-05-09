// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Limitations', {
	refresh: function(frm) {
		if (frappe.user_roles.includes("Administrator")) {
			console.log("Super Special access granted to " + frappe.session.user)
			frm.set_df_property("enable", "read_only", false);
			frm.set_df_property("company_restrictions", "read_only", false);
			frm.set_df_property("users_restrictions", "read_only", false);
			frm.set_df_property("space_restrictions", "read_only", false);
			frm.set_df_property("sms_restrictions", "read_only", false);
			frm.set_df_property("company_allowed", "read_only", false);
			frm.set_df_property("users_allowed", "read_only", false);
			frm.set_df_property("space_allowed", "read_only", false);
			frm.set_df_property("sms_allowed", "read_only", false);
			frm.set_df_property("enable_users_types_restrictions", "read_only", false);
			frm.set_df_property("enable_sms_dates", "read_only", false);
			frm.set_df_property("sms_from_date", "read_only", false);
			frm.set_df_property("sms_to_date", "read_only", false);
			frm.set_df_property("domain_restrictions", "read_only", false);
			frm.set_df_property("allowed_domains", "hidden", true);
			frm.set_df_property("end_date", "read_only", false);
			frm.set_df_property("ignore_end_date", "read_only", false);
			
		} else {
			frm.set_df_property("enable", "read_only", true);
			frm.set_df_property("company_restrictions", "read_only", true);
			frm.set_df_property("users_restrictions", "read_only", true);
			frm.set_df_property("space_restrictions", "read_only", true);
			frm.set_df_property("sms_restrictions", "read_only", true);
			frm.set_df_property("company_allowed", "read_only", true);
			frm.set_df_property("users_allowed", "read_only", true);
			frm.set_df_property("space_allowed", "read_only", true);
			frm.set_df_property("sms_allowed", "read_only", true);
			frm.set_df_property("enable_users_types_restrictions", "read_only", true);
			frm.set_df_property("enable_sms_dates", "read_only", true);
			frm.set_df_property("sms_from_date", "read_only", true);
			frm.set_df_property("sms_to_date", "read_only", true);
			frm.set_df_property("domain_restrictions", "read_only", true);
			const domains_multicheck = $(".checkbox").find("input");
			domains_multicheck.prop("disabled","true");
			frm.set_df_property("allowed_domains", "read_only", true);
			frm.set_df_property("allowed_domains", "hidden", true);
			frm.set_df_property("end_date", "read_only", true);
			frm.set_df_property("ignore_end_date", "read_only", true);
			frm.set_df_property("ignore_end_date", "hidden", true);
		}
		frm.call('get_usage_info').then( r => {
			if(r.message){
				frm.doc.active_users = r.message[0];
				frm.doc.used_space = r.message[1];
				frm.doc.active_company = r.message[2];
				frm.doc.sms_usage = r.message[3];
				frm.refresh_field('active_users');
				frm.refresh_field('used_space');
				frm.refresh_field('active_company');
				frm.refresh_field('sms_usage');
			}	
		});
		
		frm.call('get_count_type_of_user').then( r => {
			if(r.message){
				$("#types_usage").remove();
				const types_usage = $(`<div class="modal-body ui-front" id="types_usage">
						<h3>Users Types Usage :</h3>
						<table class="table table-bordered">
						<thead>
							<tr>
							<th>Type Name</th>
							<th>Active Count</th>
							<th>Allowed Count</th>
							</tr>
						</thead>
						<tbody>
						</tbody>
						</table>
					</div>`).appendTo(frm.fields_dict.types_usage.wrapper);
					const tbody = $(types_usage).find('tbody');
				r.message.forEach(element => {
					const tr = $(`
					<tr>
						<td>${element.type_name}</td>
						<td>${element.active_count}</td>
						<td>${element.allowed_count }</td>
					</tr>
					`).appendTo(tbody)
				});
			frm.refresh_field('types_usage');
			}	
		})
		frm.trigger('ignore_end_date');

	},
	before_load: function(frm) {
		if(!frm.domains_multicheck) {
			frm.domains_multicheck = frappe.ui.form.make_control({
				parent: frm.fields_dict.domains_html.$wrapper,
				df: {
					fieldname: "domains_multicheck",
					fieldtype: "MultiCheck",
					get_data: () => {
						let allowed_domains = (frm.doc.allowed_domains || []).map(row => row.domain);
						return frappe.boot.all_domains.map(domain => {
							return {
								label: domain,
								value: domain,
								checked: allowed_domains.includes(domain)
							};
						});
					}
				},
				render_input: true
			});
			frm.domains_multicheck.refresh_input();
		}
	},
	validate: function(frm) {
		frm.trigger('set_options_in_table');
	},

	set_options_in_table: function(frm) {
		let selected_options = frm.domains_multicheck.get_value();
		let unselected_options = frm.domains_multicheck.options
			.map(option => option.value)
			.filter(value => {
				return !selected_options.includes(value);
			});

		let map = {}, list = [];
		(frm.doc.allowed_domains || []).map(row => {
			map[row.domain] = row.name;
			list.push(row.domain);
		});

		unselected_options.map(option => {
			if(list.includes(option)) {
				frappe.model.clear_doc("Allowed Domains", map[option]);
			}
		});

		selected_options.map(option => {
			if(!list.includes(option)) {
				frappe.model.clear_doc("Allowed Domains", map[option]);
				let row = frappe.model.add_child(frm.doc, "Allowed Domains", "allowed_domains");
				row.domain = option;
			}
		});

		refresh_field('allowed_domains');
	},
	ignore_end_date: function(frm) {
		frm.toggle_reqd("end_date", !frm.doc.ignore_end_date ? 1:0);
	},
});

	
