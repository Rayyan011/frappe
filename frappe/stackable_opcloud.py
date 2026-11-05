"""Apply Stackable OpCloud's site branding through supported settings."""

import frappe

PRODUCT_NAME = "Stackable OpCloud"
LOGO_URL = "/assets/frappe/images/stackable-opcloud/logo.png"


def apply_branding():
	"""Run with ``bench --site SITE execute frappe.stackable_opcloud.apply_branding``."""
	frappe.only_for("System Manager")
	website = frappe.get_single("Website Settings")
	website.app_name = PRODUCT_NAME
	website.app_logo = LOGO_URL
	website.save()

	navbar = frappe.get_single("Navbar Settings")
	navbar.app_logo = LOGO_URL
	navbar.save()

	system = frappe.get_single("System Settings")
	system.app_name = PRODUCT_NAME
	system.save()
	frappe.clear_cache()
	return {"app_name": PRODUCT_NAME, "app_logo": LOGO_URL}
