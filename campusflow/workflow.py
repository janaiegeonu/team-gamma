"""Ticket lookup, staff assignment, status transitions, and Open Work Queue.

Engineer A owns this module. The older get_unresolved_queue name remains as a
compatibility wrapper, but the required queue now contains OPEN tickets only.
"""

from campusflow.validation import validate_staff_name, validate_status


PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def find_ticket(tickets, ticket_id):
    """Return a ticket by ID, matching case-insensitively, or raise ValueError."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID cannot be empty.")

    wanted_id = ticket_id.strip().upper()
    for ticket in tickets:
        stored_id = ticket.get("id")
        if isinstance(stored_id, str) and stored_id.upper() == wanted_id:
            return ticket
    raise ValueError(f"Ticket {wanted_id} was not found.")


def assign_staff(tickets, ticket_id, staff_name):
    """Assign a nonblank staff label; an open ticket starts work on assignment.

    This preserves the original CampusFlow behaviour: assigning an open ticket
    also moves it to in_progress. Reassignment of an in-progress ticket is
    allowed, but a resolved ticket must first be reopened.
    """
    cleaned_name = validate_staff_name(staff_name)
    ticket = find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise ValueError("Reopen the ticket before modifying its assignment.")
    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError("Ticket has an invalid status and cannot be assigned.")

    # No mutation occurs until every check above has passed.
    ticket["assigned_to"] = cleaned_name
    if ticket["status"] == "open":
        ticket["status"] = "in_progress"
    return ticket


def update_status(tickets, ticket_id, new_status):
    """Apply only the allowed open -> in_progress -> resolved -> open workflow."""
    target_status = validate_status(new_status)
    ticket = find_ticket(tickets, ticket_id)
    current_status = ticket.get("status")

    if current_status not in ("open", "in_progress", "resolved"):
        raise ValueError("Ticket has an invalid current status.")
    if current_status == target_status:
        raise ValueError("The ticket already has this status.")

    allowed_transition = {
        "open": "in_progress",
        "in_progress": "resolved",
        "resolved": "open",
    }
    expected_status = allowed_transition[current_status]

    if target_status != expected_status:
        raise ValueError(
            f"Cannot move a {current_status.replace('_', ' ')} ticket "
            f"directly to {target_status.replace('_', ' ')}."
        )

    if target_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError("Assign a staff member before starting the ticket.")

    # Only mutate after validating the full transition.
    ticket["status"] = target_status
    return ticket


def get_open_work_queue(tickets):
    """Return only open tickets, ordered by priority then numeric ticket ID."""
    open_tickets = [ticket for ticket in tickets if ticket.get("status") == "open"]
    return sorted(
        open_tickets,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )


def get_unresolved_queue(tickets):
    """Compatibility name for the original queue; now returns open tickets only."""
    return get_open_work_queue(tickets)
