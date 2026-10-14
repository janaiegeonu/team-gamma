"""Generate current-state ticket counts and resolution insights.

Engineer B owns this module.
"""


STATUS_VALUES = ("open", "in_progress", "resolved")
PRIORITY_VALUES = ("critical", "high", "medium", "low")
CATEGORY_VALUES = ("Network", "Hardware", "Software", "Other")


def generate_report(tickets):
    """Return total, group counts, unresolved/resolved counts, and resolution %."""
    status_counts = {status: 0 for status in STATUS_VALUES}
    priority_counts = {priority: 0 for priority in PRIORITY_VALUES}
    category_counts = {category: 0 for category in CATEGORY_VALUES}

    for ticket in tickets:
        status_counts[ticket["status"]] += 1
        priority_counts[ticket["priority"]] += 1
        category_counts[ticket["category"]] += 1

    total = len(tickets)
    resolved_count = status_counts["resolved"]
    unresolved_count = status_counts["open"] + status_counts["in_progress"]

    # The empty collection has a defined 0% result instead of division by zero.
    resolution_percentage = (resolved_count / total * 100) if total else 0

    return {
        "total": total,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_category": category_counts,
        "unresolved": unresolved_count,
        "resolved": resolved_count,
        "resolution_percentage": resolution_percentage,
    }
