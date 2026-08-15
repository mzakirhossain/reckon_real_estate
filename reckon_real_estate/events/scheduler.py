import frappe

def update_installment_statuses():
    from reckon_real_estate.sales.doctype.installment_plan.installment_plan import update_all_installment_statuses
    update_all_installment_statuses()
