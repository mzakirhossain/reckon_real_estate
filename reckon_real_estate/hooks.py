app_name = "reckon_real_estate"
app_title = "Reckon Real Estate"
app_publisher = "Reckon Technologies Ltd."
app_description = "Real Estate vertical for ERPNext"
app_email = "hello@reckon.tech"
app_license = "MIT"

add_to_apps_screen = [
    {
        "name": "reckon_real_estate",
        "title": "Real Estate",
        "route": "/app/real-estate",
    }
]

# ERPNext already depends on Frappe, so it is the only app dependency that
# needs to be declared here.
required_apps = ["erpnext"]

before_install = "reckon_real_estate.setup.install.before_install"
after_install = "reckon_real_estate.setup.install.after_install"
after_migrate = "reckon_real_estate.setup.install.after_migrate"

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
