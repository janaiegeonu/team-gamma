"""Engineer A tests for JSON validation, persistence, migration, and safe reload."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from campusflow.notes import add_note, next_note_id
from campusflow.storage import load_tickets, save_tickets, validate_ticket_data
from campusflow.tickets import create_ticket


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "tickets.json"

    def make_tickets(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi issue", "Network", "high", 10)
        add_note(tickets, "T001", "Mentor A", "Router reboot attempted")
        return tickets

    def test_save_and_load_preserve_notes_and_next_ids(self):
        tickets = self.make_tickets()
        save_tickets(tickets, self.path)
        loaded = load_tickets(self.path)
        self.assertEqual(loaded, tickets)
        self.assertEqual(next_note_id(loaded[0]), "N002")
        next_note = add_note(loaded, "T001", "Mentor B", "Switch ports checked")
        self.assertEqual(next_note["note_id"], "N002")
        create_ticket(loaded, "Laptop issue", "Hardware", "low", 1)
        self.assertEqual(loaded[-1]["id"], "T002")

    def test_missing_file_returns_empty_collection(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_empty_file_returns_empty_collection(self):
        self.path.write_text("  \n", encoding="utf-8")
        self.assertEqual(load_tickets(self.path), [])

    def test_legacy_ticket_without_notes_is_migrated_in_memory(self):
        ticket = self.make_tickets()[0].copy()
        ticket.pop("notes")
        self.path.write_text(json.dumps([ticket]), encoding="utf-8")
        loaded = load_tickets(self.path)
        self.assertEqual(loaded[0]["notes"], [])
        # Loading does not silently rewrite the original saved file.
        self.assertNotIn("notes", json.loads(self.path.read_text(encoding="utf-8"))[0])

    def test_corrupt_json_is_rejected_and_caller_memory_stays_unchanged(self):
        current = self.make_tickets()
        before = deepcopy(current)
        self.path.write_text("{ this is not json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.path)
        self.assertEqual(current, before)

    def test_duplicate_ticket_ids_reject_entire_load(self):
        ticket = self.make_tickets()[0]
        duplicate = deepcopy(ticket)
        duplicate["title"] = "Different title"
        self.path.write_text(json.dumps([ticket, duplicate]), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate ticket ID"):
            load_tickets(self.path)

    def test_priority_inconsistent_with_fields_is_rejected(self):
        ticket = self.make_tickets()[0].copy()
        ticket["priority"] = "low"
        with self.assertRaisesRegex(ValueError, "expected 'critical'"):
            validate_ticket_data([ticket])

    def test_duplicate_note_ids_within_ticket_are_rejected(self):
        ticket = self.make_tickets()[0]
        ticket["notes"].append(deepcopy(ticket["notes"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate note ID"):
            validate_ticket_data([ticket])

    def test_invalid_boolean_affected_users_is_rejected(self):
        ticket = self.make_tickets()[0].copy()
        ticket["affected_users"] = True
        with self.assertRaisesRegex(ValueError, "whole number"):
            validate_ticket_data([ticket])

    def test_invalid_status_is_rejected(self):
        ticket = self.make_tickets()[0].copy()
        ticket["status"] = "working"
        with self.assertRaisesRegex(ValueError, "Status must be"):
            validate_ticket_data([ticket])

    def test_invalid_save_does_not_overwrite_existing_file(self):
        tickets = self.make_tickets()
        save_tickets(tickets, self.path)
        original_content = self.path.read_text(encoding="utf-8")
        invalid = deepcopy(tickets)
        invalid[0]["affected_users"] = 0
        with self.assertRaises(ValueError):
            save_tickets(invalid, self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), original_content)

    def test_data_must_be_a_list(self):
        with self.assertRaisesRegex(ValueError, "expected a JSON list"):
            validate_ticket_data({"tickets": []})


if __name__ == "__main__":
    unittest.main()
