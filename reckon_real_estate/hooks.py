app_name = "reckon_real_estate"
app_title = "Reckon Real Estate"
app_publisher = "Reckon Technologies Ltd."
app_description = "Real Estate vertical for ERPNext"
app_email = "hello@reckon.tech"
app_license = "MIT"

required_apps = ["frappe", "erpnext"]

doc_events = {
    "Customer": {
        "on_update": "reckon_real_estate.events.customer.sync_customer"
    }
}

scheduler_events = {
    "daily": [
        "reckon_real_estate.events.scheduler.update_installment_statuses"
    ]
}

fixtures = []
