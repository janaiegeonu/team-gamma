"""Engineer B tests for independent quiz scoring and invalid-choice retry."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from campusflow.understanding_check import QUESTION_BANK, run_understanding_check, score_answers


class TestUnderstandingCheck(unittest.TestCase):
    def test_six_correct_answers_score_six(self):
        answers = ["B", "C", "B", "C", "C", "B"]
        self.assertEqual(score_answers(answers), 6)

    def test_wrong_or_missing_answers_do_not_score(self):
        self.assertEqual(score_answers(["A", "C"]), 1)
        self.assertEqual(score_answers([]), 0)

    def test_answers_are_case_insensitive(self):
        self.assertEqual(score_answers(["b", "c", "b", "c", "c", "b"]), 6)

    def test_invalid_choice_retries_and_final_score_uses_submitted_answers(self):
        inputs = ["X", "B", "C", "B", "C", "C", "B", "Q1 explanation", "Q2 explanation"]
        output = io.StringIO()
        with patch("builtins.input", side_effect=inputs):
            with redirect_stdout(output):
                score = run_understanding_check()
        self.assertEqual(score, 6)
        self.assertIn("Invalid choice. Please enter A, B, C, or D.", output.getvalue())
        self.assertIn("Final score: 6/6", output.getvalue())
        self.assertIn("Q1 explanation", output.getvalue())
        self.assertEqual(len(QUESTION_BANK), 6)


if __name__ == "__main__":
    unittest.main()
