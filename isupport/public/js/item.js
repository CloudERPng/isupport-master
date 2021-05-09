frappe.ui.form.on('Item', {
	sales_margin: function(frm) {
        const i = (frm.doc.sales_margin/100)/(1- (frm.doc.sales_margin/100))*100;
        // frm.set_value("sales_markup", i);
        frm.doc.sales_markup = i;
        frm.refresh_field("sales_markup");
    },
    sales_markup: function(frm) {
        const i = (frm.doc.sales_markup*100)/(100+ frm.doc.sales_markup);
        // frm.set_value("sales_margin", i);
        frm.doc.sales_margin = i;
        frm.refresh_field("sales_margin");
    },
    set_default_markup_margin: function(frm) {
            frappe.db.get_value("Item Group", {"name": frm.doc.item_group}, ["sales_margin","sales_markup"]).then(r => {
                if (r.message){
                    let values = r.message;
                    frm.doc.sales_margin = values.sales_margin || 0;
                    frm.doc.sales_markup = values.sales_markup || 0;
                    frm.refresh_field("sales_margin");
                    frm.refresh_field("sales_markup");
                    frappe.show_alert({message:__(`Sales Margin is Updated to: ${values.sales_margin}%`), indicator:'orange'}, 5);
                    frappe.show_alert({message:__(`Sales Markup is Updated to: ${values.sales_markup}%`), indicator:'orange'}, 5);
                }
            });
    },
    item_group: function(frm) {
        frm.trigger("set_default_markup_margin");
    },
    
});