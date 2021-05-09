frappe.ui.form.on('Purchase Receipt Item', {
	item_code: function(frm, cdt, cdn) {
        frm.script_manager.trigger("get_selling_rate",cdt,cdn);
    },
    rate: function(frm, cdt, cdn) {
        frm.script_manager.trigger("get_selling_rate",cdt,cdn);
    },
	get_selling_rate: function(frm, cdt, cdn) {
        const d = locals[cdt][cdn];
        frappe.db.get_value("Item", {"name": d.item_code}, "sales_markup", function(value) {
            const sales_markup = value.sales_markup || 0;
            frappe.db.get_value("Item Price", {"item_code": d.item_code, "price_list":"Standard Selling","currency":frm.doc.currency}, "price_list_rate", function(value) {
                const current_rate = value.price_list_rate;
                d.current_sale_price = current_rate;
                d.suggested_sale_price = (sales_markup * d.rate / 100) + d.rate;
                frm.refresh_field("items");
            });
        });
    },
  
});

frappe.ui.form.on('Purchase Receipt', {
	on_submit: function(frm) {
        const items = frm.doc.items;
        items.forEach(item => {
            // console.log(item);
            if (item.update_selling_price && item.suggested_sale_price) {
                frappe.db.get_value("Item Price", {"item_code": item.item_code, "price_list":"Standard Selling","currency":frm.doc.currency}, "name").then(r =>{
                    if (r.message){
                        frappe.db.set_value('Item Price',r.message.name, "price_list_rate",item.suggested_sale_price)
                            .then(r => {
                                // let doc = r.message;
                                // console.log(doc);
                                frappe.msgprint(`Standard Selling Rate for ${item.item_code} is Updated to: ${item.suggested_sale_price} ${frm.doc.currency}`)
                            });
                    } 
                    else {
                        frappe.db.insert({
                            doctype: 'Item Price',
                            item_code: item.item_code,
                            price_list: "Standard Selling",
                            currency: frm.doc.currency,
                            price_list_rate:item.suggested_sale_price,
                        }).then(doc => {
                            frappe.msgprint(`Standard Selling Rate for ${item.item_code} is Created to: ${item.suggested_sale_price} ${frm.doc.currency}`)
                            })
                    }
                });
            }
        });
    },
  
  
});