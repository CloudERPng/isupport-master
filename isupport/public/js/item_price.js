frappe.ui.form.on('Item Price', {
    refresh: function (frm) {
        frm.current_rate = parseFloat(frm.doc.price_list_rate);
   },
    onload: function (frm) {
         frm.current_rate = parseFloat(frm.doc.price_list_rate);
    },
	validate: function(frm) {
        if (frm.current_rate != frm.doc.price_list_rate) {
            frm.doc.previous_rate = frm.current_rate;
            frm.refresh_field("previous_rate");
        }
    },
    
});