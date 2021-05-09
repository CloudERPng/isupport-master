frappe.query_reports["Exchange Currency Report"] = {
    "filters": [
         {
            "fieldname":"from_date",
            "label":("From Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.add_days(frappe.datetime.get_today(), -1),
           "reqd":1
        },
         {
            "fieldname":"to_date",
            "label":("To Date"),
            "fieldtype":"Date",
            "default":get_today(),
           "reqd":1
        },
]
};