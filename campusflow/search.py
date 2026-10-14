"""Read-only ticket search with optional combined filters.

Engineer B owns this module. A search produces a new result list and never
changes ticket records or the original collection order.
"""

from campusflow.validation import (
    validate_category,
    validate_priority,
    validate_status,
)
from campusflow.workflow import PRIORITY_ORDER


def search_tickets(tickets, query="", category=None, status=None, priority=None):
    """Return tickets matching every supplied filter (logical AND).

    ``query`` performs case-insensitive title substring matching. Empty filters
    are ignored. Invalid nonempty filter options raise a friendly ValueError.
    """
    if not isinstance(query, str):
        raise ValueError("Search title must be text.")
    cleaned_query = query.strip().casefold()

    cleaned_category = None
    if category is not None and str(category).strip():
        cleaned_category = validate_category(category)

    cleaned_status = None
    if status is not None and str(status).strip():
        cleaned_status = validate_status(status)

    cleaned_priority = None
    if priority is not None and str(priority).strip():
        cleaned_priority = validate_priority(priority)

    results = []
    for ticket in tickets:
        if cleaned_query and cleaned_query not in ticket["title"].casefold():
            continue
        if cleaned_category is not None and ticket["category"] != cleaned_category:
            continue
        if cleaned_status is not None and ticket["status"] != cleaned_status:
            continue
        if cleaned_priority is not None and ticket["priority"] != cleaned_priority:
            continue
        results.append(ticket)

    return results


def sort_search_results_by_priority(tickets):
    """Return a new list sorted by priority, then numeric ticket ID."""
    return sorted(
        tickets,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )
