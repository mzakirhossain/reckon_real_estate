import frappe
from frappe.utils import flt, today


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {"label":"Date","fieldname":"date","fieldtype":"Date","width":105},
        {"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":150},
        {"label":"Unit","fieldname":"unit","fieldtype":"Link","options":"Real Estate Unit","width":120},
        {"label":"Type","fieldname":"transaction_type","fieldtype":"Data","width":130},
        {"label":"Source","fieldname":"reference","fieldtype":"Dynamic Link","options":"reference_doctype","width":150},
        {"label":"Accounting Voucher","fieldname":"voucher","fieldtype":"Dynamic Link","options":"voucher_type","width":165},
        {"label":"Debit","fieldname":"debit","fieldtype":"Currency","width":120},
        {"label":"Credit","fieldname":"credit","fieldtype":"Currency","width":120},
        {"label":"Outstanding","fieldname":"outstanding","fieldtype":"Currency","width":125},
        {"label":"GL Status","fieldname":"gl_status","fieldtype":"Data","width":95},
    ]
    booking_filters = {"customer": filters.customer, "docstatus": ["!=", 2]}
    if filters.project:
        booking_filters["project"] = filters.project
    if filters.unit:
        booking_filters["unit"] = filters.unit
    bookings = frappe.get_all("Property Booking", filters=booking_filters,
        fields=["name","customer","project","unit","booking_date","contract_value","discount","net_contract_value","booking_money"])
    booking_map = {row.name: row for row in bookings}
    booking_names = list(booking_map)
    data = []

    invoice_filters = {"customer": filters.customer, "docstatus": 1}
    if booking_names and frappe.get_meta("Sales Invoice").has_field("real_estate_booking"):
        invoice_filters["real_estate_booking"] = ["in", booking_names]
    invoices = frappe.get_all("Sales Invoice", filters=invoice_filters,
        fields=["name","posting_date","customer","grand_total","outstanding_amount",
            "real_estate_booking","real_estate_unit"])
    for invoice in invoices:
        booking = booking_map.get(invoice.real_estate_booking)
        if not booking:
            continue
        data.append({"date":invoice.posting_date,"customer":invoice.customer,"project":booking.project,
            "unit":booking.unit,"transaction_type":"Sales Invoice","reference":booking.name,
            "reference_doctype":"Property Booking","voucher":invoice.name,"voucher_type":"Sales Invoice",
            "debit":invoice.grand_total,"credit":0,"outstanding":invoice.outstanding_amount,"gl_status":"Posted"})

    collection_filters = {"customer": filters.customer, "docstatus": 1}
    if filters.project:
        collection_filters["project"] = filters.project
    if filters.unit:
        collection_filters["unit"] = filters.unit
    collections = frappe.get_all("Collection Entry", filters=collection_filters,
        fields=["name","collection_date","customer","project","unit","booking","amount","payment_entry","accounting_status"])
    total_collection = 0
    for collection in collections:
        payment = None
        if collection.payment_entry:
            payment = frappe.db.get_value("Payment Entry", collection.payment_entry,
                ["docstatus","payment_type","paid_amount"], as_dict=True)
        posted = payment and payment.docstatus == 1
        credit = flt(payment.paid_amount) if posted and payment.payment_type == "Receive" else 0
        if posted and payment.payment_type == "Pay":
            credit = -flt(payment.paid_amount)
        total_collection += credit
        data.append({"date":collection.collection_date,"customer":collection.customer,"project":collection.project,
            "unit":collection.unit,"transaction_type":"Collection","reference":collection.name,
            "reference_doctype":"Collection Entry","voucher":collection.payment_entry,"voucher_type":"Payment Entry",
            "debit":0,"credit":credit,"outstanding":0,"gl_status":"Posted" if posted else collection.accounting_status})

    data.sort(key=lambda row: (str(row.get("date") or ""), row.get("transaction_type") or ""))
    contract_value = sum(flt(row.contract_value) for row in bookings)
    discount = sum(flt(row.discount) for row in bookings)
    net_contract = sum(flt(row.net_contract_value) for row in bookings)
    booking_money = sum(flt(row.booking_money) for row in bookings)
    installment_paid = max(total_collection - booking_money, 0)
    outstanding = sum(flt(row.outstanding_amount) for row in invoices)
    overdue = 0
    if booking_names:
        overdue = frappe.db.sql("""select coalesce(sum(s.outstanding),0) from `tabInstallment Schedule` s
            join `tabInstallment Plan` p on p.name=s.parent
            where p.booking in %(bookings)s and p.docstatus=1 and s.due_date<%(today)s and s.outstanding>0""",
            {"bookings": booking_names, "today": today()})[0][0]
    summary = [
        {"label":"Contract Value","value":contract_value,"datatype":"Currency"},
        {"label":"Discount","value":discount,"datatype":"Currency"},
        {"label":"Net Contract","value":net_contract,"datatype":"Currency"},
        {"label":"Booking Money","value":booking_money,"datatype":"Currency"},
        {"label":"Installments Paid","value":installment_paid,"datatype":"Currency"},
        {"label":"ERPNext Collections","value":total_collection,"datatype":"Currency"},
        {"label":"ERPNext Outstanding","value":outstanding,"datatype":"Currency"},
        {"label":"Operational Overdue","value":overdue,"datatype":"Currency"},
    ]
    return columns, data, None, None, summary
