"""Validated, safe JSON persistence for CampusFlow.

Engineer A owns this module. Files are decoded and the complete collection is
validated before a caller can replace its active in-memory collection.
"""

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path

from campusflow.tickets import calculate_priority
from campusflow.validation import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    VALID_URGENCIES,
    validate_affected_users,
    validate_category,
    validate_note_author,
    validate_note_id,
    validate_note_message,
    validate_priority,
    validate_status,
    validate_ticket_id,
    validate_title,
    validate_urgency,
)


def _record_error(errors, location, field, message):
    """Add a consistently formatted field-level validation error."""
    errors.append(f"{location}, '{field}': {message}")


def validate_ticket_data(tickets):
    """Validate a complete list of tickets, including unique IDs and notes.

    This function collects useful errors instead of stopping at the first bad
    field. It does not repair or mutate the supplied ticket collection.
    """
    if not isinstance(tickets, list):
        raise ValueError("Invalid ticket data: expected a JSON list.")

    errors = []
    seen_ticket_ids = set()
    required_fields = {
        "id", "title", "category", "urgency", "affected_users",
        "priority", "status", "assigned_to", "notes",
    }

    for index, ticket in enumerate(tickets):
        location = f"Ticket at position {index + 1}"
        if not isinstance(ticket, dict):
            errors.append(f"{location}: expected a ticket object.")
            continue

        missing = sorted(required_fields - set(ticket))
        for field in missing:
            errors.append(f"{location}: missing '{field}'.")
        if missing:
            # Continue checking present fields, but skip dependent validation
            # if a required value is absent.
            pass

        ticket_id = ticket.get("id")
        if "id" in ticket:
            try:
                validate_ticket_id(ticket_id)
                if ticket_id in seen_ticket_ids:
                    _record_error(errors, location, "id", f"duplicate ticket ID {ticket_id!r}.")
                else:
                    seen_ticket_ids.add(ticket_id)
            except ValueError as error:
                _record_error(errors, location, "id", str(error))

        title = ticket.get("title")
        if "title" in ticket:
            try:
                validate_title(title)
            except ValueError as error:
                _record_error(errors, location, "title", str(error))

        category = ticket.get("category")
        if "category" in ticket:
            try:
                normalized_category = validate_category(category)
                if category != normalized_category:
                    _record_error(
                        errors, location, "category",
                        f"use the canonical value {normalized_category!r}.",
                    )
            except ValueError as error:
                _record_error(errors, location, "category", str(error))

        urgency = ticket.get("urgency")
        if "urgency" in ticket:
            try:
                normalized_urgency = validate_urgency(urgency)
                if urgency != normalized_urgency:
                    _record_error(errors, location, "urgency", "must use lowercase canonical values.")
            except ValueError as error:
                _record_error(errors, location, "urgency", str(error))

        affected_users = ticket.get("affected_users")
        if "affected_users" in ticket:
            try:
                validate_affected_users(affected_users)
            except ValueError as error:
                _record_error(errors, location, "affected_users", str(error))

        priority = ticket.get("priority")
        if "priority" in ticket:
            try:
                normalized_priority = validate_priority(priority)
                if priority != normalized_priority:
                    _record_error(errors, location, "priority", "must use lowercase canonical values.")
            except ValueError as error:
                _record_error(errors, location, "priority", str(error))

        status = ticket.get("status")
        if "status" in ticket:
            try:
                normalized_status = validate_status(status)
                if status != normalized_status:
                    _record_error(errors, location, "status", "must use lowercase canonical values.")
            except ValueError as error:
                _record_error(errors, location, "status", str(error))

        if "assigned_to" in ticket:
            assigned_to = ticket["assigned_to"]
            if assigned_to is not None and (
                not isinstance(assigned_to, str) or not assigned_to.strip()
            ):
                _record_error(
                    errors, location, "assigned_to",
                    "must be null or a nonempty staff label.",
                )

        # A priority must agree with urgency and affected_users, not merely be
        # one of the accepted strings.
        if (
            isinstance(urgency, str)
            and urgency in VALID_URGENCIES
            and type(affected_users) is int
            and affected_users > 0
            and isinstance(priority, str)
            and priority in VALID_PRIORITIES
        ):
            expected_priority = calculate_priority(urgency, affected_users)
            if priority != expected_priority:
                _record_error(
                    errors, location, "priority",
                    f"expected {expected_priority!r} for the stored urgency and affected_users.",
                )

        notes = ticket.get("notes")
        if "notes" in ticket:
            if not isinstance(notes, list):
                _record_error(errors, location, "notes", "must be a list.")
            else:
                seen_note_ids = set()
                for note_index, note in enumerate(notes):
                    note_location = f"{location}, note {note_index + 1}"
                    if not isinstance(note, dict):
                        errors.append(f"{note_location}: expected a note object.")
                        continue

                    for field in ("note_id", "author", "message"):
                        if field not in note:
                            errors.append(f"{note_location}: missing '{field}'.")

                    note_id = note.get("note_id")
                    if "note_id" in note:
                        try:
                            validate_note_id(note_id)
                            if note_id in seen_note_ids:
                                errors.append(f"{note_location}: duplicate note ID {note_id!r} within this ticket.")
                            else:
                                seen_note_ids.add(note_id)
                        except ValueError as error:
                            errors.append(f"{note_location}, 'note_id': {error}")

                    if "author" in note:
                        try:
                            validate_note_author(note["author"])
                        except ValueError as error:
                            errors.append(f"{note_location}, 'author': {error}")

                    if "message" in note:
                        try:
                            validate_note_message(note["message"])
                        except ValueError as error:
                            errors.append(f"{note_location}, 'message': {error}")

    if errors:
        raise ValueError("Ticket data validation failed:\n- " + "\n- ".join(errors))
    return True


def save_tickets(tickets, file_path):
    """Validate then atomically replace the JSON file with the ticket list.

    A temporary file is written in the same directory and renamed only after
    JSON serialization succeeds. Invalid data never overwrites the target file.
    """
    validate_ticket_data(tickets)
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f"{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(tickets, temporary_file, indent=4, ensure_ascii=False)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        temporary_path.replace(path)
    except (OSError, TypeError, ValueError) as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        if isinstance(error, TypeError):
            raise ValueError(f"Ticket data cannot be saved as JSON: {error}") from error
        raise


def _prepare_loaded_tickets(decoded_data):
    """Copy decoded data and migrate the old schema by adding empty note lists.

    The first CampusFlow version did not store notes. Adding notes=[] to those
    old records preserves existing tickets without modifying the source file.
    Other invalid or missing fields are not silently repaired.
    """
    if not isinstance(decoded_data, list):
        return decoded_data

    migrated = deepcopy(decoded_data)
    for ticket in migrated:
        if isinstance(ticket, dict):
            ticket.setdefault("notes", [])
    return migrated


def load_tickets(file_path):
    """Read and validate tickets; return a new list only after full validation.

    A missing or empty file represents an empty collection, preserving the
    behaviour of the original application. A bad file raises ValueError and
    never mutates a caller's current in-memory collection.
    """
    path = Path(file_path)
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        raise

    if not content.strip():
        return []

    try:
        decoded_data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"Cannot load tickets: {path} contains invalid JSON.") from error

    tickets = _prepare_loaded_tickets(decoded_data)
    validate_ticket_data(tickets)
    return tickets
