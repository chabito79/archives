# Copyright (c) 2013, Web Notes Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AlreadyRegistered(frappe.ValidationError): pass

class Registrant(Document):
	def before_insert(self):
		if frappe.db.get_value("Registrant", {"email_id": self.email_id}):
			raise AlreadyRegistered
