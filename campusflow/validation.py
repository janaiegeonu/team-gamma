"""Shared validation helpers for CampusFlow ticket and note data.

Engineer A owns this module. Keeping the basic rules here prevents the CLI,
workflow functions, and JSON loader from gradually adopting different rules.
"""

import re


# Canonical values accepted by the application.
VALID_CATEGORIES = ("Network", "Hardware", "Software", "Other")
VALID_URGENCIES = ("low", "medium", "high")
VALID_PRIORITIES = ("critical", "high", "medium", "low")
VALID_STATUSES = ("open", "in_progress", "resolved")

_TICKET_ID_PATTERN = re.compile(r"^T\d{3,}$")
_NOTE_ID_PATTERN = re.compile(r"^N\d{3,}$")


def validate_title(title):
    """Return a trimmed title or raise ValueError for invalid input."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title cannot be empty.")
    return title.strip()


def validate_category(category):
    """Return a canonical category; category matching ignores letter case."""
    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    cleaned = category.strip().casefold()
    for valid_category in VALID_CATEGORIES:
        if cleaned == valid_category.casefold():
            return valid_category

    allowed = ", ".join(VALID_CATEGORIES)
    raise ValueError(f"Category must be one of: {allowed}.")


def validate_urgency(urgency):
    """Return a lowercase urgency or raise ValueError."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    cleaned = urgency.strip().lower()
    if cleaned not in VALID_URGENCIES:
        raise ValueError("Urgency must be low, medium, or high.")
    return cleaned


def validate_affected_users(affected_users):
    """Require a strictly positive int; reject bools, floats, and strings."""
    # bool is a subclass of int in Python, so an isinstance check alone is
    # not strict enough for this business rule.
    if type(affected_users) is not int:
        raise ValueError("Affected users must be a whole number (not text or a decimal).")
    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero.")
    return affected_users


def validate_staff_name(staff_name):
    """Return a trimmed staff label or reject a blank/non-text value."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")
    return staff_name.strip()


def validate_status(status):
    """Return a canonical lowercase status."""
    if not isinstance(status, str):
        raise ValueError("Status must be text.")
    cleaned = status.strip().lower()
    if cleaned not in VALID_STATUSES:
        raise ValueError("Status must be open, in_progress, or resolved.")
    return cleaned


def validate_priority(priority):
    """Return a canonical lowercase priority."""
    if not isinstance(priority, str):
        raise ValueError("Priority must be text.")
    cleaned = priority.strip().lower()
    if cleaned not in VALID_PRIORITIES:
        raise ValueError("Priority must be critical, high, medium, or low.")
    return cleaned


def validate_ticket_id(ticket_id):
    """Validate IDs such as T001 and T120; T000 is not a valid generated ID."""
    if not isinstance(ticket_id, str) or not _TICKET_ID_PATTERN.fullmatch(ticket_id):
        raise ValueError("Ticket ID must use the format T001, T002, and so on.")
    if int(ticket_id[1:]) < 1:
        raise ValueError("Ticket ID number must be greater than zero.")
    return ticket_id


def validate_note_id(note_id):
    """Validate note IDs such as N001 and N120."""
    if not isinstance(note_id, str) or not _NOTE_ID_PATTERN.fullmatch(note_id):
        raise ValueError("Note ID must use the format N001, N002, and so on.")
    if int(note_id[1:]) < 1:
        raise ValueError("Note ID number must be greater than zero.")
    return note_id


def validate_note_author(author):
    """Return a trimmed note author or reject a blank label."""
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author cannot be empty.")
    return author.strip()


def validate_note_message(message):
    """Return a trimmed note message containing 5 through 300 characters."""
    if not isinstance(message, str):
        raise ValueError("Note message must be text.")

    cleaned = message.strip()
    if len(cleaned) < 5:
        raise ValueError("Note message must contain at least 5 characters.")
    if len(cleaned) > 300:
        raise ValueError("Note message cannot exceed 300 characters.")
    return cleaned
