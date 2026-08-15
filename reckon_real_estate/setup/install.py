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
    validate_installation()


def after_migrate():
    """Recheck the schema after an app update or framework migration."""
    validate_installation()


def validate_installation():
    """Return the supported stack details or raise a clear repair action."""
    stack = validate_supported_stack()
    missing = [doctype for doctype in REQUIRED_DOCTYPES if not frappe.db.exists("DocType", doctype)]
    if missing:
        frappe.throw(
            "Reckon Real Estate schema is incomplete. Run `bench --site <site> migrate`. "
            f"Missing DocTypes: {', '.join(missing)}"
        )
    return stack
