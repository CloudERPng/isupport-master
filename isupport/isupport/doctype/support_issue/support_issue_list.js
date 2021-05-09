frappe.listview_settings['Support Issue'] = {
	filters: [["status", "!=", "Closed"]],
	get_indicator: function(doc) {
		var colors = {
			"Open": "red",
			"Assigned": "orange",
			"Closed": "green",
		}
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	},
};
