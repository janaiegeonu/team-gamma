"""Engineer A tests for structured note creation and lifecycle rules."""

import unittest
from copy import deepcopy

from campusflow.notes import add_note, get_ticket_notes, next_note_id
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_staff, update_status


class TestNotes(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi issue", "Network", "high", 5)

    def test_valid_note_gets_n001_and_trimmed_values(self):
        note = add_note(self.tickets, "T001", " Mentor A ", " Router reboot attempted ")
        self.assertEqual(note, {
            "note_id": "N001",
            "author": "Mentor A",
            "message": "Router reboot attempted",
        })

    def test_blank_author_is_rejected_without_mutation_or_id_use(self):
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "author"):
            add_note(self.tickets, "T001", "  ", "Router reboot attempted")
        self.assertEqual(self.tickets, before)
        self.assertEqual(next_note_id(self.tickets[0]), "N001")

    def test_short_note_is_rejected_without_consuming_id(self):
        add_note(self.tickets, "T001", "Mentor", "First note")
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "at least 5"):
            add_note(self.tickets, "T001", "Mentor", "  ok  ")
        self.assertEqual(self.tickets, before)
        self.assertEqual(next_note_id(self.tickets[0]), "N002")

    def test_message_over_300_characters_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "300"):
            add_note(self.tickets, "T001", "Mentor", "x" * 301)
        self.assertEqual(self.tickets[0]["notes"], [])

    def test_resolved_ticket_rejects_note_but_reopened_ticket_accepts_it(self):
        add_note(self.tickets, "T001", "Mentor A", "First note added")
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "only be added"):
            add_note(self.tickets, "T001", "Mentor B", "Follow-up rejected")
        self.assertEqual(self.tickets, before)

        update_status(self.tickets, "T001", "open")
        note = add_note(self.tickets, "T001", "Mentor B", "Follow-up after reopen")
        self.assertEqual(note["note_id"], "N002")
        self.assertEqual(len(self.tickets[0]["notes"]), 2)

    def test_next_note_id_uses_highest_existing_numeric_id(self):
        self.tickets[0]["notes"] = [
            {"note_id": "N001", "author": "A", "message": "First valid note"},
            {"note_id": "N005", "author": "B", "message": "Another valid note"},
        ]
        self.assertEqual(next_note_id(self.tickets[0]), "N006")

    def test_view_notes_are_sorted_and_detached_from_ticket_data(self):
        self.tickets[0]["notes"] = [
            {"note_id": "N002", "author": "B", "message": "Second note"},
            {"note_id": "N001", "author": "A", "message": "First note"},
        ]
        view = get_ticket_notes(self.tickets, "T001")
        self.assertEqual([note["note_id"] for note in view], ["N001", "N002"])
        view[0]["message"] = "changed outside"
        self.assertEqual(self.tickets[0]["notes"][1]["message"], "First note")


if __name__ == "__main__":
    unittest.main()
