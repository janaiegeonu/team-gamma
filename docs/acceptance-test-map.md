# Acceptance-test map

| Assignment acceptance case | Main test location | Evidence asserted |
|---|---|---|
| Priority precedence | `tests/test_tickets.py` | Critical is chosen before the broad high rule |
| Unassigned open -> in progress rejected | `tests/test_workflow.py` | Exception plus exact unchanged state |
| Resolved assignment mutation rejected | `tests/test_workflow.py` | Exception plus unchanged collection |
| Invalid affected-users types/ranges | `tests/test_validation.py`, `tests/test_tickets.py`, `tests/test_storage.py` | Zero, negative, float, string, and bool rejected |
| Note creation and ID | `tests/test_notes.py` | Valid `N001` structure and trimming |
| Invalid note does not consume ID | `tests/test_notes.py` | Collection snapshot and unchanged next ID |
| Resolved note rejected, reopen allows note | `tests/test_notes.py` | Rejection preserves history; next valid note succeeds |
| Case-insensitive title search | `tests/test_search.py` | Mixed case and substring result |
| Combined filters use AND | `tests/test_search.py` | Only a record passing every supplied filter remains |
| Empty report uses 0% | `tests/test_reports.py` | No divide-by-zero and percentage equals zero |
| Report totals after reopen | `tests/test_reports.py` | Current statuses drive counts |
| Save/load preserves notes and IDs | `tests/test_storage.py` | Loaded notes equal saved notes; next IDs do not collide |
| Corrupt/duplicate-ID JSON rejected | `tests/test_storage.py` | Load raises and existing caller data remains intact |
| Quiz retries invalid choice and scores | `tests/test_understanding_check.py` | Invalid answer retries; six actual correct answers score 6 |
| CLI rejects invalid menu choice | `tests/test_cli.py` | Helpful error, then clean exit |

The complete suite should be run with `python -m unittest discover -s tests -v` from the project root.
