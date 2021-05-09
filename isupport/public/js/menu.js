$(document).on('app_ready', function() {
    // waiting for page to load completely
   
        const route = frappe.get_route();
 
            frappe.ui.form.on(route[1], {
                setup: function (frm) {
                    frm.trigger("new_support_issue");
                },
                onload: function (frm) {
                    frm.trigger("new_support_issue");
                },
                refresh: function (frm) {
                    frm.trigger("new_support_issue");
                },
                before_load: function (frm) {
                    frm.trigger("new_support_issue");
                },
                new_support_issue: function (frm) {
                    if (route[0] == "Form") {
                        cur_frm.page.add_menu_item(__("New Support Issue"), function() {
                            frappe.new_doc('Support Issue');
                        });
                    }
                },
            });
            
            frappe.listview_settings[route[1]] = {
                onload: function (listview) {
 
                    listview.page.add_menu_item(__("New Support Issue"), function() {
                        frappe.new_doc('Support Issue');
                    });
                    cur_list.page.add_menu_item(__("New Support Issue"), function() {
                        frappe.new_doc('Support Issue');
                    });
                },
            };
    
});