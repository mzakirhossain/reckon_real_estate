import frappe

def get_data():
    return [
        {
            "module_name": "Reckon Property Management",
            "type": "module",
            "label": "Property Management",
            "color": "blue",
            "icon": "home",
        },
        {
            "module_name": "Reckon Sales",
            "type": "module",
            "label": "Real Estate Sales",
            "color": "green",
            "icon": "shopping-cart",
        },
        {
            "module_name": "Reckon Collection",
            "type": "module",
            "label": "Collection",
            "color": "orange",
            "icon": "money",
        },
        {
            "module_name": "Reckon Reports",
            "type": "module",
            "label": "Real Estate Reports",
            "color": "purple",
            "icon": "chart",
        },
    ]
