"""Engineer A tests for ticket creation, ID generation, and priority rules."""

import unittest

from campusflow.tickets import calculate_priority, create_ticket, generate_ticket_id


class TestPriorityCalculation(unittest.TestCase):
    def test_critical_rule_precedes_broader_high_rule(self):
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("high", 15), "critical")

    def test_high_urgency_with_few_users_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_ten_or_more_users_with_medium_urgency_is_high(self):
        self.assertEqual(calculate_priority("medium", 10), "high")

    def test_medium_rule_uses_urgency_or_three_users(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_rule(self):
        self.assertEqual(calculate_priority("low", 1), "low")


class TestTicketCreation(unittest.TestCase):
    def test_create_ticket_has_notes_and_expected_fields(self):
        tickets = []
        ticket = create_ticket(tickets, "Wi-Fi issue", "network", "high", 10)
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(ticket["notes"], [])
        self.assertEqual(len(tickets), 1)

    def test_invalid_create_does_not_change_collection(self):
        tickets = []
        before = [ticket.copy() for ticket in tickets]
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Broken", "Unknown", "high", 3)
        self.assertEqual(tickets, before)

    def test_create_rejects_boolean_affected_users_without_append(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Wi-Fi", "Network", "high", True)
        self.assertEqual(tickets, [])

    def test_next_ticket_id_uses_highest_number_not_list_length(self):
        tickets = [
            {"id": "T002"},
            {"id": "T014"},
            {"id": "T007"},
        ]
        self.assertEqual(generate_ticket_id(tickets), "T015")


if __name__ == "__main__":
    unittest.main()
