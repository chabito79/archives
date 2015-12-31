import frappe
from frappe.frappeclient import FrappeClient

def migrate():
	print "connecting..."
	frappe.flags.mute_emails = True
	remote = FrappeClient("https://erpnext.com", "Administrator", frappe.conf.erpnext_admin_password)
	remote.migrate_doctype("Help Category")
	remote.migrate_doctype("Help Article")
	remote.migrate_single("Knowledge Base Settings")
	frappe.flags.mute_emails = False