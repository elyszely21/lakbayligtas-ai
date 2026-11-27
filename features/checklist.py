"""Static outdoor gear catalog and Markdown checklist export."""

GEAR_CATALOG = {
    "Hiking": {
        "Shelter": (
            {"id": "emergency-bivy", "name": "Emergency bivy or shelter", "priority": "optional"},
        ),
        "Sleeping": (
            {"id": "emergency-blanket", "name": "Emergency blanket", "priority": "optional"},
        ),
        "Food and water": (
            {"id": "water-bottle", "name": "Reusable water bottle", "priority": "essential"},
            {"id": "trail-snacks", "name": "Trail snacks", "priority": "essential"},
        ),
        "Safety": (
            {"id": "first-aid-kit", "name": "Small first-aid kit", "priority": "essential"},
            {"id": "headlamp", "name": "Headlamp with spare batteries", "priority": "essential"},
            {"id": "whistle", "name": "Emergency whistle", "priority": "optional"},
        ),
        "Clothing": (
            {"id": "hiking-footwear", "name": "Comfortable hiking footwear", "priority": "essential"},
            {"id": "rain-layer", "name": "Weather-appropriate rain layer", "priority": "essential"},
            {"id": "extra-socks", "name": "Extra pair of socks", "priority": "optional"},
        ),
        "Responsible travel / Leave No Trace": (
            {"id": "waste-bag", "name": "Bag for packing out all rubbish", "priority": "essential"},
            {"id": "stay-on-trail", "name": "Stay on marked trails", "priority": "essential"},
            {"id": "respect-wildlife", "name": "Respect wildlife and local communities", "priority": "essential"},
        ),
    },
    "Camping": {
        "Shelter": (
            {"id": "tent", "name": "Tent with all poles and stakes", "priority": "essential"},
            {"id": "groundsheet", "name": "Groundsheet or footprint", "priority": "optional"},
        ),
        "Sleeping": (
            {"id": "sleeping-bag", "name": "Sleeping bag suitable for the trip", "priority": "essential"},
            {"id": "sleeping-pad", "name": "Sleeping pad", "priority": "optional"},
        ),
        "Food and water": (
            {"id": "water-container", "name": "Reusable water container", "priority": "essential"},
            {"id": "camp-meals", "name": "Food for the planned stay", "priority": "essential"},
            {"id": "cookware", "name": "Reusable cookware and utensils", "priority": "optional"},
        ),
        "Safety": (
            {"id": "first-aid-kit", "name": "Small first-aid kit", "priority": "essential"},
            {"id": "headlamp", "name": "Headlamp with spare batteries", "priority": "essential"},
            {"id": "whistle", "name": "Emergency whistle", "priority": "optional"},
        ),
        "Clothing": (
            {"id": "camp-footwear", "name": "Comfortable outdoor footwear", "priority": "essential"},
            {"id": "warm-layer", "name": "Warm layer for the evening", "priority": "essential"},
            {"id": "extra-clothes", "name": "Spare dry clothes", "priority": "optional"},
        ),
        "Responsible travel / Leave No Trace": (
            {"id": "waste-bag", "name": "Bag for packing out all rubbish", "priority": "essential"},
            {"id": "camp-on-durable-ground", "name": "Use designated or durable camping areas", "priority": "essential"},
            {"id": "respect-wildlife", "name": "Respect wildlife and local communities", "priority": "essential"},
        ),
    },
    "Trekking": {
        "Shelter": (
            {"id": "tent", "name": "Lightweight tent or approved shelter", "priority": "essential"},
            {"id": "repair-kit", "name": "Small shelter repair kit", "priority": "optional"},
        ),
        "Sleeping": (
            {"id": "sleeping-bag", "name": "Sleeping bag suitable for the trip", "priority": "essential"},
            {"id": "sleeping-pad", "name": "Compact sleeping pad", "priority": "optional"},
        ),
        "Food and water": (
            {"id": "water-bottles", "name": "Reusable water bottles or reservoir", "priority": "essential"},
            {"id": "trail-food", "name": "Food for each planned day", "priority": "essential"},
            {"id": "water-treatment", "name": "Water treatment method for the route", "priority": "optional"},
        ),
        "Safety": (
            {"id": "first-aid-kit", "name": "Small first-aid kit", "priority": "essential"},
            {"id": "headlamp", "name": "Headlamp with spare batteries", "priority": "essential"},
            {"id": "navigation", "name": "Map or offline navigation device", "priority": "essential"},
            {"id": "whistle", "name": "Emergency whistle", "priority": "optional"},
        ),
        "Clothing": (
            {"id": "trek-footwear", "name": "Broken-in trekking footwear", "priority": "essential"},
            {"id": "layering-system", "name": "Weather-appropriate clothing layers", "priority": "essential"},
            {"id": "extra-socks", "name": "Extra pair of socks", "priority": "optional"},
        ),
        "Responsible travel / Leave No Trace": (
            {"id": "waste-bag", "name": "Bag for packing out all rubbish", "priority": "essential"},
            {"id": "stay-on-trail", "name": "Stay on marked trails", "priority": "essential"},
            {"id": "respect-wildlife", "name": "Respect wildlife and local communities", "priority": "essential"},
        ),
    },
    "Sightseeing": {
        "Shelter": (
            {"id": "sun-rain-cover", "name": "Compact sun or rain cover", "priority": "optional"},
        ),
        "Sleeping": (),
        "Food and water": (
            {"id": "water-bottle", "name": "Reusable water bottle", "priority": "essential"},
            {"id": "snack", "name": "Light snack", "priority": "optional"},
        ),
        "Safety": (
            {"id": "phone", "name": "Charged phone with emergency contacts", "priority": "essential"},
            {"id": "first-aid-kit", "name": "Small first-aid kit", "priority": "optional"},
        ),
        "Clothing": (
            {"id": "walking-footwear", "name": "Comfortable walking footwear", "priority": "essential"},
            {"id": "sun-protection", "name": "Sun-protective clothing or hat", "priority": "optional"},
        ),
        "Responsible travel / Leave No Trace": (
            {"id": "waste-bag", "name": "Bag for packing out all rubbish", "priority": "essential"},
            {"id": "respect-sites", "name": "Respect signs, wildlife, and local communities", "priority": "essential"},
        ),
    },
}


def export_markdown(activity, checked_items=()):
    """Export a complete activity checklist, marking the checked item IDs."""
    if activity not in GEAR_CATALOG:
        raise ValueError(f"Unknown activity: {activity}")

    checked = set(checked_items)
    lines = [f"# {activity} Gear Checklist", ""]
    for priority in ("essential", "optional"):
        lines.extend([f"## {priority.title()} items", ""])
        for group, items in GEAR_CATALOG[activity].items():
            matching_items = [item for item in items if item["priority"] == priority]
            if not matching_items:
                continue
            lines.extend([f"### {group}", ""])
            for item in matching_items:
                mark = "x" if item["id"] in checked else " "
                lines.append(f"- [{mark}] {item['name']}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
