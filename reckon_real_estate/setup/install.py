"""Frappe/ERPNext installation checks for supported platform versions."""

from importlib import import_module

import frappe


SUPPORTED_MAJOR_VERSIONS = {"15", "16"}
REQUIRED_DOCTYPES = (
    "Real Estate Project",
    "Real Estate Building",
    "Real Estate Floor",
    "Real Estate Unit",
    "Property Booking",
    "Installment Plan",
    "Installment Schedule",
    "Collection Entry",
    "Payment Allocation",
)
ERPNext_MASTER_DOCTYPES = (
    "Customer",
    "Company",
    "Project",
    "Cost Center",
    "Item",
)
LEGACY_MODULES = (
    "Reckon Property Management",
    "Reckon Sales",
    "Reckon Collection",
    "Reckon Reports",
)


def _major_version(app_name):
    """Return an app's major version without adding a packaging dependency."""
    version = getattr(import_module(app_name), "__version__", "")
    major = str(version).split(".", 1)[0]
    if not major.isdigit():
        frappe.throw(f"Could not determine the {app_name.title()} version: {version!r}.")
    return major


def validate_supported_stack():
    """Require matching Frappe and ERPNext v15 or v16 installations."""
    frappe_major = _major_version("frappe")
    erpnext_major = _major_version("erpnext")

    if frappe_major not in SUPPORTED_MAJOR_VERSIONS:
        frappe.throw("Reckon Real Estate supports Frappe v15 and v16 only.")
    if erpnext_major not in SUPPORTED_MAJOR_VERSIONS:
        frappe.throw("Reckon Real Estate supports ERPNext v15 and v16 only.")
    if frappe_major != erpnext_major:
        frappe.throw(
            "Frappe and ERPNext must use the same major version "
            f"(found Frappe v{frappe_major}, ERPNext v{erpnext_major})."
        )

    return {"frappe": frappe_major, "erpnext": erpnext_major}


def before_install():
    """Stop a site installation early if its framework stack is unsupported."""
    validate_supported_stack()


def after_install():
    """Confirm that app schema sync created every Release 1 DocType."""
    cleanup_legacy_modules()
    validate_installation()


def after_migrate():
    """Recheck the schema after an app update or framework migration."""
    cleanup_legacy_modules()
    validate_installation()


def cleanup_legacy_modules():
    """Remove empty module definitions created by pre-consolidation releases."""
    for module in LEGACY_MODULES:
        if frappe.db.get_value("Module Def", module, "app_name") != "reckon_real_estate":
            continue
        if frappe.db.exists("DocType", {"module": module}):
            continue
        frappe.delete_doc("Module Def", module, force=True, ignore_permissions=True)


def validate_installation():
    """Verify custom schema and the ERPNext masters linked by this app."""
    stack = validate_supported_stack()
    missing = [doctype for doctype in REQUIRED_DOCTYPES if not frappe.db.exists("DocType", doctype)]
    if missing:
        frappe.throw(
            "Reckon Real Estate schema is incomplete. Run `bench --site <site> migrate`. "
            f"Missing DocTypes: {', '.join(missing)}"
        )
    missing_erpnext = [
        doctype for doctype in ERPNext_MASTER_DOCTYPES if not frappe.db.exists("DocType", doctype)
    ]
    if missing_erpnext:
        frappe.throw(
            "The required ERPNext master DocTypes are unavailable. "
            f"Missing: {', '.join(missing_erpnext)}"
        )
    return stack
