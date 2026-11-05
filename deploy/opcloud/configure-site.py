"""Run once inside the production bench, before starting public web services."""
import json
import os
from pathlib import Path

site = "opcloud.amplii.online"
sites = Path("/home/frappe/frappe-bench/sites")
common = {
    "db_host": "db",
    "db_port": 3306,
    "redis_cache": "redis://redis-cache:6379",
    "redis_queue": "redis://redis-queue:6379",
    "redis_socketio": "redis://redis-queue:6379",
    "socketio_port": 9000,
    "socketio_backend": "node",
    "developer_mode": 0,
    "server_script_enabled": 0,
    "host_name": "https://opcloud.amplii.online",
    "mute_emails": 1,
    "max_file_size": 10485760,
    "keep_backups_for_hours": 168,
}
(sites / "common_site_config.json").write_text(json.dumps(common, indent=2))

if os.environ.get("OPCLOUD_AFTER_RESTORE") == "1":
    import frappe
    from frappe.utils.password import update_password

    credentials = json.loads(Path("/transfer/credentials.json").read_text())
    original = json.loads(next(Path("/transfer").glob("*-site_config_backup.json")).read_text())
    config_file = sites / site / "site_config.json"
    config = json.loads(config_file.read_text())
    if original.get("encryption_key"):
        config["encryption_key"] = original["encryption_key"]
    config.update({"developer_mode": 0, "server_script_enabled": 0,
                   "host_name": common["host_name"], "mute_emails": 1})
    config_file.write_text(json.dumps(config, indent=2))
    config_file.chmod(0o600)

    os.chdir(sites)
    frappe.init(site=site, sites_path=str(sites))
    frappe.connect()
    frappe.set_user("Administrator")
    for user, key in [("Administrator", "administrator_password"),
                      ("testuser@gmail.com", "test_user_password")]:
        update_password(user, credentials[key], logout_all_sessions=True)
    # Local OAuth grants must not become cloud credentials after migration.
    for doctype in ("OAuth Bearer Token", "OAuth Authorization Code"):
        if frappe.db.exists("DocType", doctype):
            frappe.db.delete(doctype)
    frappe.db.set_single_value("Website Settings", "disable_signup", 1)
    frappe.db.set_single_value("System Settings", "login_with_email_link", 0)
    from frappe.stackable_opcloud import apply_branding
    apply_branding()
    logo = "/assets/frappe/images/stackable-opcloud/logo.png"
    for settings in ("FCRM Settings", "HD Settings"):
        if frappe.db.exists("DocType", settings):
            frappe.db.set_single_value(settings, "brand_name", "Stackable OpCloud")
            frappe.db.set_single_value(settings, "brand_logo", logo)
    frappe.db.commit()
    print("Production passwords replaced; branding applied; old OAuth grants removed.")
    print("Installed apps:", ", ".join(frappe.get_installed_apps()))
    print("Projects:", frappe.db.count("Project"))
    print("Support tickets:", frappe.db.count("HD Ticket"))
    frappe.destroy()
