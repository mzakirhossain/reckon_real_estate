def get_data():
    return {
        "internal_links": {
            "Collection Entry": ["installment_plan", "name"],
            "Sales Invoice": ["sales_invoice", "name"],
        },
        "non_standard_fieldnames": {"Payment Entry": "installment_plan"},
        "transactions": [{"label": "Accounting", "items": ["Sales Invoice", "Collection Entry", "Payment Entry"]}],
    }
