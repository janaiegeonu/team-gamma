"""Engineer B tests for case-insensitive, combined, read-only ticket search."""

import unittest
from copy import deepcopy

from campusflow.search import search_tickets, sort_search_results_by_priority
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_staff, update_status


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Campus Wi-Fi failing", "Network", "high", 12)  # critical/open
        create_ticket(self.tickets, "WiFi access point", "Network", "medium", 2)  # medium/open
        create_ticket(self.tickets, "Wi-Fi laptop adapter", "Hardware", "low", 1)  # low/open
        assign_staff(self.tickets, "T002", "Ada")
        update_status(self.tickets, "T002", "resolved")

    def test_title_substring_search_ignores_case(self):
        result = search_tickets(self.tickets, query="WI-FI")
        self.assertEqual([ticket["id"] for ticket in result], ["T001", "T003"])

    def test_casefold_handles_unicode_case_expansion(self):
        # Bug-hunter edge case for Engineer B: casefold makes Straße/STRASSE
        # compare equivalently, unlike a basic ASCII-only lowercase assumption.
        tickets = []
        create_ticket(tickets, "Straße network issue", "Network", "low", 1)
        self.assertEqual([ticket["id"] for ticket in search_tickets(tickets, query="STRASSE")], ["T001"])

    def test_combined_filters_use_and(self):
        result = search_tickets(
            self.tickets,
            query="wi-fi",
            category="Network",
            status="open",
            priority="critical",
        )
        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_ticket_matching_only_some_filters_is_excluded(self):
        result = search_tickets(self.tickets, query="wifi", category="Network", status="resolved")
        self.assertEqual([ticket["id"] for ticket in result], ["T002"])

    def test_empty_filters_do_not_restrict_collection(self):
        self.assertEqual(len(search_tickets(self.tickets)), 3)
        self.assertEqual(len(search_tickets(self.tickets, category=" ", status="")), 3)

    def test_invalid_filter_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Category must be one of"):
            search_tickets(self.tickets, category="Security")

    def test_search_does_not_mutate_records_or_collection_order(self):
        before = deepcopy(self.tickets)
        search_tickets(self.tickets, query="wifi", category="Network")
        self.assertEqual(self.tickets, before)

    def test_priority_view_sorts_priority_then_numeric_id(self):
        result = sort_search_results_by_priority(self.tickets)
        self.assertEqual([ticket["id"] for ticket in result], ["T001", "T002", "T003"])


if __name__ == "__main__":
    unittest.main()
