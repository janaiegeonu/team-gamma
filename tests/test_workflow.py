"""Engineer A tests for assignment, status transitions, and the Open Work Queue."""

import unittest
from copy import deepcopy

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_staff,
    get_open_work_queue,
    get_unresolved_queue,
    update_status,
)


def make_ticket(tickets, title, category, urgency, affected_users):
    return create_ticket(tickets, title, category, urgency, affected_users)


class TestAssignmentAndTransitions(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        make_ticket(self.tickets, "Wi-Fi problem", "Network", "high", 12)

    def test_assignment_starts_work_on_open_ticket(self):
        ticket = assign_staff(self.tickets, "T001", " Ada ")
        self.assertEqual(ticket["assigned_to"], "Ada")
        self.assertEqual(ticket["status"], "in_progress")

    def test_blank_staff_is_rejected_without_mutation(self):
        before = deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            assign_staff(self.tickets, "T001", "   ")
        self.assertEqual(self.tickets, before)

    def test_unknown_ticket_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            assign_staff(self.tickets, "T999", "Ada")

    def test_unassigned_open_ticket_cannot_enter_progress(self):
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "Assign a staff member"):
            update_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets, before)

    def test_in_progress_ticket_can_be_resolved(self):
        assign_staff(self.tickets, "T001", "Ada")
        self.assertEqual(update_status(self.tickets, "T001", "resolved")["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")
        self.assertEqual(update_status(self.tickets, "T001", "open")["status"], "open")

    def test_resolved_ticket_assignment_change_is_rejected_without_mutation(self):
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "Reopen"):
            assign_staff(self.tickets, "T001", "Grace")
        self.assertEqual(self.tickets, before)

    def test_open_ticket_cannot_skip_directly_to_resolved(self):
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "Cannot move"):
            update_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets, before)

    def test_same_status_is_rejected_without_mutation(self):
        before = deepcopy(self.tickets)
        with self.assertRaisesRegex(ValueError, "already has"):
            update_status(self.tickets, "T001", "open")
        self.assertEqual(self.tickets, before)


class TestOpenWorkQueue(unittest.TestCase):
    def test_queue_includes_only_open_sorted_by_priority_then_numeric_id(self):
        tickets = []
        make_ticket(tickets, "High 1", "Network", "high", 2)   # T001 high
        make_ticket(tickets, "Critical", "Network", "high", 10) # T002 critical
        make_ticket(tickets, "High 2", "Hardware", "high", 1)   # T003 high
        make_ticket(tickets, "Low", "Other", "low", 1)          # T004 low
        assign_staff(tickets, "T003", "Ada")  # T003 is now in_progress
        assign_staff(tickets, "T004", "Grace")
        update_status(tickets, "T004", "resolved")

        ids = [ticket["id"] for ticket in get_open_work_queue(tickets)]
        self.assertEqual(ids, ["T002", "T001"])
        self.assertEqual([ticket["id"] for ticket in get_unresolved_queue(tickets)], ids)

    def test_queue_does_not_reorder_original_collection(self):
        tickets = []
        make_ticket(tickets, "Low", "Other", "low", 1)
        make_ticket(tickets, "Critical", "Network", "high", 10)
        original_ids = [ticket["id"] for ticket in tickets]
        get_open_work_queue(tickets)
        self.assertEqual([ticket["id"] for ticket in tickets], original_ids)

    def test_numeric_ticket_id_tie_break_does_not_sort_t010_before_t002(self):
        # Bug-hunter edge case for Engineer A: lexical ID sorting would put
        # T010 before T002, but the requirement is numeric ordering.
        tickets = []
        for number in range(1, 11):
            make_ticket(tickets, f"Issue {number}", "Other", "low", 1)
        queue_ids = [ticket["id"] for ticket in get_open_work_queue(tickets)]
        self.assertEqual(queue_ids, [f"T{number:03d}" for number in range(1, 11)])

    def test_empty_queue(self):
        self.assertEqual(get_open_work_queue([]), [])


if __name__ == "__main__":
    unittest.main()
