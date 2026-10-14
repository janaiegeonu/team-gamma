"""Ticket creation, field validation, priority calculation, and ticket IDs.

Engineer A owns this module.
"""

from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)


def calculate_priority(urgency, affected_users):
    """Calculate priority using the original CampusFlow rule order."""
    # The most specific rule must come first: both conditions make a ticket
    # critical, even though it also satisfies the broader high-priority rule.
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def validate_ticket(title, category, urgency, affected_users):
    """Validate create-ticket input and return its canonical field values."""
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)
    return title, category, urgency


def _ticket_number(ticket_id):
    """Return the numeric part of a valid-looking T-number; invalid IDs sort low."""
    if isinstance(ticket_id, str) and ticket_id.startswith("T"):
        suffix = ticket_id[1:]
        if suffix.isdigit():
            return int(suffix)
    return 0


def generate_ticket_id(tickets):
    """Generate an ID greater than every numeric ticket ID already present."""
    highest_number = 0
    for ticket in tickets:
        if isinstance(ticket, dict):
            number = _ticket_number(ticket.get("id", ""))
            highest_number = max(highest_number, number)
    return f"T{highest_number + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate data and append a new open ticket; invalid input changes nothing."""
    # All user data is checked before the list is changed.
    title, category, urgency = validate_ticket(
        title, category, urgency, affected_users
    )
    ticket_id = generate_ticket_id(tickets)

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    tickets.append(ticket)
    return ticket
