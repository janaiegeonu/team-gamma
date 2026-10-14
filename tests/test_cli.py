"""Engineer B smoke tests for main-menu interaction and CLI feedback."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main


class TestMainCLI(unittest.TestCase):
    def test_invalid_menu_choice_is_reported_and_exit_works(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(main, "DATA_FILE", Path(folder) / "tickets.json"):
                output = io.StringIO()
                with patch("builtins.input", side_effect=["12", "11"]):
                    with redirect_stdout(output):
                        main.main()
        self.assertIn("Invalid choice. Please enter a number from 1 to 11.", output.getvalue())
        self.assertIn("Thank you for using CampusFlow Next!", output.getvalue())

    def test_bad_saved_data_stops_startup_without_overwriting_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            path.write_text("not json", encoding="utf-8")
            original = path.read_text(encoding="utf-8")
            with patch.object(main, "DATA_FILE", path):
                output = io.StringIO()
                with redirect_stdout(output):
                    result = main.load_tickets_for_application()
            self.assertIsNone(result)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertIn("The saved file was not changed", output.getvalue())

    def test_create_ticket_through_cli_saves_valid_json(self):
        import json

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data" / "tickets.json"
            with patch.object(main, "DATA_FILE", path):
                output = io.StringIO()
                # Menu: create ticket, then exit. The title/category/urgency/
                # affected-user inputs are consumed by the create-ticket view.
                inputs = ["1", "Wi-Fi problem", "1", "3", "12", "11"]
                with patch("builtins.input", side_effect=inputs):
                    with redirect_stdout(output):
                        main.main()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]["id"], "T001")
            self.assertEqual(saved[0]["notes"], [])
            self.assertIn("created successfully", output.getvalue())


if __name__ == "__main__":
    unittest.main()
