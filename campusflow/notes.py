"""Safe creation and read-only viewing of ticket follow-up notes.

Engineer A owns the note data/business rules. The CLI is implemented by B.
The tickets collection is passed explicitly, consistent with the existing
CampusFlow functions and avoiding hidden global application state.
"""

from copy import deepcopy

from campusflow.validation import (
    validate_note_author,
    validate_note_id,
    validate_note_message,
)
from campusflow.workflow import find_ticket


def next_note_id(ticket):
    """Return the next per-ticket note ID after the highest existing numeric ID."""
    highest_number = 0
    for note in ticket.get("notes", []):
        note_id = note.get("note_id", "") if isinstance(note, dict) else ""
        if isinstance(note_id, str) and note_id.startswith("N"):
            suffix = note_id[1:]
            if suffix.isdigit():
                highest_number = max(highest_number, int(suffix))
    return f"N{highest_number + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a validated note to an open/in-progress ticket and return the note.

    A rejected note does not modify the collection or consume a note ID.
    """
    ticket = find_ticket(tickets, ticket_id)

    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError("Notes can only be added to open or in-progress tickets. Reopen this ticket first.")

    cleaned_author = validate_note_author(author)
    cleaned_message = validate_note_message(message)

    if not isinstance(ticket.get("notes"), list):
        raise ValueError("Ticket notes data is invalid; notes must be a list.")

    # The ID is determined after validation, so invalid attempts never consume it.
    note = {
        "note_id": next_note_id(ticket),
        "author": cleaned_author,
        "message": cleaned_message,
    }
    validate_note_id(note["note_id"])
    ticket["notes"].append(note)
    return note


def get_ticket_notes(tickets, ticket_id):
    """Return detached copies of a ticket's notes in numeric ID order."""
    ticket = find_ticket(tickets, ticket_id)
    notes = sorted(
        ticket.get("notes", []),
        key=lambda note: int(note["note_id"][1:]),
    )
    # Returning copies means callers can display notes without gaining a way
    # to mutate the underlying ticket through the returned list.
    return deepcopy(notes)
