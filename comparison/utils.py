def generate_product_name(labels):
     if not labels or not isinstance(labels, list):
        return "Unknown Product"

    # Get the top label
     raw = labels[0].replace("_", " ").lower()

    # Mapping: convert raw ML labels into better product names
     mapping = {
        "microphone": "Microphone",
        "headphones": "Bluetooth Headphones",
        "headphone": "Bluetooth Headphones",
        "speaker": "Bluetooth Speaker",
        "tv": "Smart TV",
        "television": "Smart TV",
        "laptop": "Laptop",
        "computer": "Desktop Computer",
        "keyboard": "Mechanical Keyboard",
        "mouse": "Wireless Mouse",
        "mobile": "Smartphone",
        "phone": "Smartphone",
        "camera": "Digital Camera",
        "watch": "Smart Watch",
        "bottle": "Water Bottle",
        "shoe": "Running Shoes",
        "shoes": "Running Shoes",
        "bag": "Backpack",
        "dress": "Women Dress",
        "fan": "Table Fan",
        "mixer": "Mixer Grinder",
        "bulb": "LED Light Bulb",
        "shirt": "Men Shirt",
        "tshirt": "Men T-Shirt",
        "earphone": "In-Ear Earphones",
        "projector": "LED Projector",
        "charger": "Mobile Charger",
        "router": "Wi-Fi Router",
        "printer": "Color Printer",
    }

    # If exact match found, return mapped name
     if raw in mapping:
        return mapping[raw]

    # Capitalize words as fallback
     return raw.title()


def clean_label(label: str) -> str:
    """
    Helper: Clean individual label string safely
    """
    if not label:
        return ""

    return label.replace("_", " ").title()