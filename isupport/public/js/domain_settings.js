// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Domain Settings', {
	refresh: function(frm) {
        frappe.call({
            "method": "isupport.limitations.doctype.site_limitations.site_limitations.get_allowed_domains",
            callback: function(r) {
                if(r.message && r.message.length) {
                    frappe.show_alert({message:__('Some Domains is restricted!'), indicator:'orange'}, 5);
                    const span = $(".checkbox").find("span.label-area.small");
                    span.each(function() {
                        if (r.message.includes($(this).attr('data-unit'))) {
                            const input = $(this).closest("div").find("input");
                            input.removeAttr("disabled");
                        } else {
                            const input = $(this).closest("div").find("input");
                            input.prop("disabled","true");
                        }
                    });
                }
            }
        });
	},

});
