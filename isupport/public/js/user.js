frappe.ui.form.on('User', {
	refresh: function(frm) {
        frm.trigger("type_of_user");
    },

    type_of_user: function (frm) {
        if (frm.is_new()) {
            return
        }
        const user_roles = $(".frappe-control .user-role").find('input');
        const user_modules = $(".row .module-block-list").find('input');
        user_roles.prop("disabled","true")
        user_modules.prop("disabled","true")
        frappe.call({
            "method": "isupport.limitations.doctype.utype.utype.get_allowed_roles",
            "args": {
                "type_name": frm.doc.type_of_user
            },
            callback: function(r) {
                if(r.message && r.message.length) {
                    if (r.message[1] == 1){
                        frm.set_df_property("role_profile_name", "read_only", false);
                        user_roles.removeAttr("disabled");
                    } else {
                        user_roles.prop('checked', false);
                        frm.set_value("role_profile_name", "");
                        frm.set_df_property("role_profile_name", "read_only", true);
                        r.message[0].forEach(element => {
                            const element_role = $(`[data-user-role='${element}']`);
                            element_role.find('input').removeAttr("disabled");
                            element_role.find('input').prop('checked', true);
                            });
                    }
                }
            }
        });
        frappe.call({
            "method": "isupport.limitations.doctype.utype.utype.get_allowed_modules",
            "args": {
                "type_name": frm.doc.type_of_user
            },
            callback: function(r) {
                if(r.message && r.message.length) {
                    if (r.message[1] == 1){
                        user_modules.removeAttr("disabled");
                        user_modules.prop('checked', true);
                        frm.clear_table("block_modules");
                    } else {
                        user_modules.prop('checked', false);
                        r.message[0].forEach(element => {
                            const element_module = $(`[data-module='${element}']`);
                            element_module.removeAttr("disabled");
                            element_module.prop('checked', true);
                            // me.frm.add_child("block_modules", {"module": element});
                            });
                    }
                    const u_modules = $(".row .module-block-list").find('input');
                    frm.clear_table("block_modules");
                    u_modules.each(function () {
                        if($(this).prop("checked") == false) {
                            me.frm.add_child("block_modules", {"module": this.getAttribute('data-module')});
                        }
                    });
                }
            }
        });
    },
    
    validate : function(frm) {
        frm.trigger("type_of_user");
    }
});


cur_frm.set_query("type_of_user", function() {
	return{
		"filters": [
			["UType", "enable", "=", "1"],
		]
	}
});