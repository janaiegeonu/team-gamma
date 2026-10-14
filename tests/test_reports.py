"""Engineer B tests for complete report totals and analytics."""

import unittest

from campusflow.reports import generate_report
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_staff, update_status


class TestReports(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi problem", "Network", "high", 15)
        create_ticket(self.tickets, "Projector issue", "Hardware", "medium", 4)
        create_ticket(self.tickets, "App issue", "Software", "low", 1)
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")

    def test_total_status_priority_and_category_counts(self):
        report = generate_report(self.tickets)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_status"], {
            "open": 2, "in_progress": 0, "resolved": 1,
        })
        self.assertEqual(report["by_priority"], {
            "critical": 1, "high": 0, "medium": 1, "low": 1,
        })
        self.assertEqual(report["by_category"], {
            "Network": 1, "Hardware": 1, "Software": 1, "Other": 0,
        })

    def test_unresolved_and_resolution_percentage(self):
        report = generate_report(self.tickets)
        self.assertEqual(report["unresolved"], 2)
        self.assertEqual(report["resolved"], 1)
        self.assertAlmostEqual(report["resolution_percentage"], 100 / 3)

    def test_empty_report_has_zero_percent(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["resolution_percentage"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertTrue(all(value == 0 for value in report["by_category"].values()))

    def test_reopened_ticket_is_counted_by_current_status(self):
        update_status(self.tickets, "T001", "open")
        report = generate_report(self.tickets)
        self.assertEqual(report["by_status"]["open"], 3)
        self.assertEqual(report["by_status"]["resolved"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["unresolved"], 3)
        self.assertEqual(report["resolution_percentage"], 0)

    def test_report_does_not_change_ticket_status(self):
        before = [ticket["status"] for ticket in self.tickets]
        generate_report(self.tickets)
        self.assertEqual([ticket["status"] for ticket in self.tickets], before)


if __name__ == "__main__":
    unittest.main()
