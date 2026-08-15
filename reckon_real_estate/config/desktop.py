import frappe

def get_data():
    return [
        {
            "module_name": "Property Management",
            "type": "module",
            "label": "Property Management",
            "color": "blue",
            "icon": "home",
        },
        {
            "module_name": "Sales",
            "type": "module",
            "label": "Real Estate Sales",
            "color": "green",
            "icon": "shopping-cart",
        },
        {
            "module_name": "Collection",
            "type": "module",
            "label": "Collection",
            "color": "orange",
            "icon": "money",
        },
        {
            "module_name": "Reports",
            "type": "module",
            "label": "Real Estate Reports",
            "color": "purple",
            "icon": "chart",
        },
    ]
