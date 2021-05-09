frappe.ui.form.on('Item Group', {
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
});