# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals 
import frappe
from frappe.model.document import Document
from frappe.utils import get_url_to_form, get_url
from frappe import _
import json
import requests
from isupport.tools import print_out
from frappe.desk.form.utils import add_comment
from frappe.utils import today, format_datetime, now, nowdate, getdate, get_url, get_host_name
from time import sleep
from frappe.utils.change_log import get_versions
from frappe.chat.doctype.chat_message.chat_message import send

class ToObject(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)


@frappe.whitelist(allow_guest=True)
def receive_init(*args, **kwargs):
    r = frappe.request
    body = r.get_data()
    message = {}
    
    if body :
        data = body.decode('utf-8')
        msgs =  ToObject(data)
        atr_list = list(msgs.__dict__)

        for atr in atr_list:
            if getattr(msgs, atr) :
                message[atr] = getattr(msgs, atr)
    else:
        print_out(message)
    doc = frappe.get_doc({
        "doctype": "Support Issue",
        "subject": message["subject"],
        "support_code": message["name"],
        "issue_type": message["issue_type"],
        "owner_user": message["owner_user"],
        "owner_user_name": message["owner_user_name"],
        "issue_date": message["issue_date"],
        "priority": message["priority"],
        "is_billable": message["is_billable"],
        "customization_fees": message["customization_fees"],
        "currency": message["currency"],
    })
    doc.flags.ignore_permissions = True
    doc.save()
    return doc.name


def add_transaction_comment(doc):
    if not doc.is_new():
        if doc.last_message:
            add_comment(
                doc.doctype, 
                doc.name,
                doc.last_message, 
                "guest",
                "guest",
            )


def creat_log(message):
    doc = frappe.get_doc("Support Issue",message["client_code"])
    new_log_row = doc.append('issue_log', {})
    new_log_row.from_user = message["from_user"]
    new_log_row.from_name = message["from_name"]
    new_log_row.notes = message["notes"]
    new_log_row.date = message["date"]
    new_log_row.time = message["time"]
    if "error_msg" in message and message["error_msg"] and message["error_msg"] != "":
        new_log_row.error_msg = message["error_msg"]
    frappe.db.commit()
    doc.last_message = message["last_message"]
    doc.flags.ignore_permissions = True
    doc.save()
    doc.reload()
    add_transaction_comment(doc)
    return doc.name



@frappe.whitelist(allow_guest=True)
def receive_message(*args, **kwargs):
    r = frappe.request
    body = r.get_data()
    message = {}
    if body :
        data = body.decode('utf-8')
        msgs =  ToObject(data)
        atr_list = list(msgs.__dict__)

        for atr in atr_list:
            if getattr(msgs, atr) :
                message[atr] = getattr(msgs, atr)
    else:
        print_out(message)
    
    if not "client_code" in message:
        return False

    doc_name = creat_log(message)
    return doc_name




@frappe.whitelist(allow_guest=True)
def receive_changes(*args, **kwargs):
    r = frappe.request
    body = r.get_data()
    headers = r.headers
    space = "\n" * 2
    message = {}
    url = get_url(r.url)
    if body :
        data = body.decode('utf-8')
        msgs =  ToObject(data)
        atr_list = list(msgs.__dict__)

        for atr in atr_list:
            if getattr(msgs, atr) :
                message[atr] = getattr(msgs, atr)
    else:
        print_out(message)
    
    if not "client_code" in message:
        return False

    notife_message = ""     
    doc = frappe.get_doc("Support Issue",message["client_code"])
    if doc.status != message["status"]:
        notife_message += "Status to: {0} . ".format(message["status"])
        doc.status = message["status"]
    if doc.subject != message["subject"]:
        notife_message += "Subject to: {0} . ".format(message["subject"])
        doc.subject = message["subject"]
    if doc.priority != message["priority"]:
        notife_message += "Priority to: {0} . ".format(message["priority"])
        doc.priority = message["priority"]
    if doc.issue_type != message["issue_type"]:
        notife_message += "Issue Type to: {0} . ".format(message["issue_type"])
        doc.issue_type = message["issue_type"]
    if "due_date" in message and str(doc.due_date) != message["due_date"]:
        notife_message += "Due Date to: {0} . ".format(message["due_date"])
        doc.due_date = message["due_date"]

    if message["is_billable"] != "No" and int(doc.is_billable) != int(message["is_billable"]):
        notife_message += "Is Billable to: {0} . ".format(message["is_billable"])
        doc.is_billable = message["is_billable"]
    elif doc.is_billable  and message["is_billable"] == "No":
        notife_message += "Remove Is Billable . "
        doc.is_billable = 0

    if message["customization_fees"] != "No" and float(doc.customization_fees) != float(message["customization_fees"]):
        notife_message += "Customization Fees to: {0} . ".format(message["customization_fees"])
        doc.customization_fees = message["customization_fees"]
    elif doc.customization_fees and message["customization_fees"] == "No":
        notife_message += "Remove Customization Fees . "
        doc.customization_fees = 0
    
    if message["customization_description"] != "No" and doc.customization_description != message["customization_description"]:
        notife_message += "Customization Description to: {0} . ".format(message["customization_description"])
        doc.customization_description = message["customization_description"]
    elif doc.customization_description and message["customization_description"] == "No":
        notife_message += "Remove Customization Description . "
        doc.customization_description = ""

    if message["invoiced"] == "Yes":
        notife_message += "Invoiced to: {0} . ".format(message["invoiced"])
        doc.invoiced = 1

    if "currency" in message and doc.currency != message["currency"]:
        notife_message += "Currency to: {0} . ".format(message["currency"])
        doc.currency = message["currency"]

    if message["status"] == "Closed":
        doc.closed_by_support = 1
        doc.reopen_by_support = 0
    elif (message["status"] == "Open" or message["status"] == "Assigned") and doc.closed_by_support ==1:
        doc.reopen_by_support = 1
        doc.closed_by_support = 0
    doc.edited_user = message["from_user"]
    doc.edited_user_name = message["from_name"]
    doc.flags.ignore_permissions = True
    doc.save()
    doc.reload()
    if notife_message:
        message["notes"] = "{0} Changed : ".format(message["from_name"]) + notife_message
        message["last_message"] = message["notes"]
        creat_log(message)
    return doc.name


def send_caht(doc, method):
    support_code = frappe.get_value('Chat Room Support Code', doc.room,"support_code")
    support_user = check_caht_users(doc.room)
    if support_user:
        if support_code:
            send_message(doc,support_code)
        else:
            send_init_sync(doc,support_user)



def check_caht_users(room_name):
    users = frappe.get_all('Chat Room User',
			filters={'parent': room_name},
			fields=['*']
		)
    for user in users:
        if "support" in user.user:
            return user.user



def send_init_sync(doc,support_user):
    if frappe.session.user == "Guest":
        return
    url = frappe.get_value("ISupport Settings",None,"support_url")
    if not url:
        return
    url = str(url) + "/api/method/usupport.sync.receive_init"
    user_name = frappe.get_value("User",doc.user,"full_name")
    data = {
        "name":  doc.room,
        "is_chat": 1,
        "subject": "Chat {} {}".format(user_name, doc.room),
        "priority": "Medium",
        "versions": get_version(),
        "url": get_host_name(),
        "issue_type": "Chat Support",
        "owner_user": doc.user,
        "owner_user_name": user_name,
        "issue_date": today(),
        "support_user":support_user,
    }
    for i in range(3):
        try:
            r = requests.post(url, data=json.dumps(data), timeout=5)
            r.raise_for_status()
            frappe.logger().debug({"webhook_success": r.text})
            support_code = json.loads(r.text)["message"]
            # print_out(support_code)
            room_doc = frappe.get_doc({
                "doctype": "Chat Room Support Code",
                "room": doc.room,
                "support_code": support_code,
            })
            room_doc.flags.ignore_permissions = True
            room_doc.save()
            send_message(doc,support_code)
            break
        except Exception as e:
            frappe.logger().debug({"webhook_error": e, "try": i + 1})
            sleep(3 * i + 1)
            if i != 2:
                continue
            else:
                raise e



def send_message(doc,support_code):
        if frappe.session.user == "Guest":
            return
        url = frappe.get_value("ISupport Settings",None,"support_url")
        if not url:
            return
        url = str(url) + "/api/method/usupport.sync.receive_message"
        space = "\n" * 2
        user_name = frappe.get_value("User",doc.user,"full_name")
        message = "{0} {1}From: {2}".format(doc.content,space,user_name)
        data = {
            "name": doc.name,
            "support_code": support_code,
            "notes": doc.content,
            "last_message": message,
            "from_user": frappe.session.user,
            "from_name": user_name,
            "date": nowdate(),
            "time": now(),
        }
        for i in range(3):
            try:
                r = requests.post(url, data=json.dumps(data), timeout=5)
                r.raise_for_status()
                frappe.logger().debug({"webhook_success": r.text})
                break
            except Exception as e:
                frappe.logger().debug({"webhook_error": e, "try": i + 1})
                sleep(3 * i + 1)
                if i != 2:
                    continue
                else:
                    raise e



def get_version():
    version = ""
    space = "\n"
    for key,value in get_versions().items():
        version = version + value["title"] + " " + value["branch"]+" "+value["version"] + space
    return version


@frappe.whitelist(allow_guest=True)
def receive_chat_message(*args, **kwargs):
    r = frappe.request
    body = r.get_data()
    message = {}
    if body :
        data = body.decode('utf-8')
        msgs =  ToObject(data)
        atr_list = list(msgs.__dict__)

        for atr in atr_list:
            if getattr(msgs, atr) :
                message[atr] = getattr(msgs, atr)
    else:
        print_out(message)
    
    if not "room" in message:
        return False

    send(
        user = message["user"],
        room = message["room"],
        content = message["content"],
        type = "Content"
    )
    return True