from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Support"),
			"items": [
				{
					"type": "doctype",
					"name": "Support Issue",
					"onboard": 1,
				},
			]
		},
		{
			"label": _("Licensing Information"),
			"items": [
				{
					"type": "doctype",
					"name": "Site Limitations",
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "UType",
					"onboard": 1,
				},
				
			]
		},
		
		
	]
