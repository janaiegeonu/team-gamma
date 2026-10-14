"""Engineer A tests for common field-validation rules."""

import unittest

from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_note_message,
    validate_staff_name,
    validate_ticket_id,
    validate_title,
    validate_urgency,
)


class TestValidation(unittest.TestCase):
    def test_title_is_trimmed(self):
        self.assertEqual(validate_title("  Wi-Fi issue  "), "Wi-Fi issue")

    def test_blank_title_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "title cannot be empty"):
            validate_title("   ")

    def test_category_is_normalized_to_canonical_value(self):
        self.assertEqual(validate_category(" hardware "), "Hardware")

    def test_unknown_category_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Category must be one of"):
            validate_category("Spaceship")

    def test_urgency_is_normalized(self):
        self.assertEqual(validate_urgency(" HIGH "), "high")

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_urgency("urgent")

    def test_affected_users_must_be_positive_integer(self):
        self.assertEqual(validate_affected_users(3), 3)
        for value in (0, -1, 2.5, "3", True, False):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_affected_users(value)

    def test_staff_label_is_trimmed_and_blank_rejected(self):
        self.assertEqual(validate_staff_name(" Ada "), "Ada")
        with self.assertRaises(ValueError):
            validate_staff_name("  ")

    def test_ticket_id_format_and_number(self):
        self.assertEqual(validate_ticket_id("T001"), "T001")
        for value in ("T1", "T000", "ticket-1", "N001", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_ticket_id(value)

    def test_note_message_uses_trimmed_length(self):
        self.assertEqual(validate_note_message("  tried  "), "tried")
        with self.assertRaisesRegex(ValueError, "at least 5"):
            validate_note_message("  ok ")
        with self.assertRaisesRegex(ValueError, "300"):
            validate_note_message("x" * 301)


if __name__ == "__main__":
    unittest.main()
