# Engineer ownership and integration contract

The ownership split below keeps the code review boundaries clear. Engineer A and Engineer B must both write code and tests, and both must understand the integrated application.

## Engineer A — ticket safety and storage

| Files | Responsibility |
|---|---|
| `campusflow/validation.py` | Shared field and note validation, canonical values, ID formats |
| `campusflow/tickets.py` | Ticket creation, priority precedence, ticket ID generation |
| `campusflow/workflow.py` | Lookup, assignment, allowed status transitions, Open Work Queue |
| `campusflow/notes.py` | Note creation, note ID generation, read-only note viewing |
| `campusflow/storage.py` | Complete data validation, JSON save/load, legacy notes migration, safe replacement |
| `tests/test_validation.py` | Validation rules and boundary values |
| `tests/test_tickets.py` | Priority and ticket-creation regression tests |
| `tests/test_workflow.py` | Assignment, lifecycle, state-preservation, and Open Work Queue tests |
| `tests/test_notes.py` | Note constraints, status safety, and ID continuity |
| `tests/test_storage.py` | JSON schema, duplicate IDs, invalid files, and reload tests |

## Engineer B — search, reports, and CLI

| Files | Responsibility |
|---|---|
| `campusflow/search.py` | Case-insensitive title substring search, combined filters, optional priority ordering |
| `campusflow/reports.py` | Status/priority/category counts, resolution percentage, empty-dataset behaviour |
| `campusflow/understanding_check.py` | Question bank, input validation, independent scoring function |
| `main.py` | Menus, input retry, friendly CLI errors, display, and integration with Engineer A's APIs |
| `tests/test_search.py` | Case-insensitivity, AND filtering, invalid filters, read-only behaviour, result sorting |
| `tests/test_reports.py` | Report counts, current status after reopen, empty report |
| `tests/test_understanding_check.py` | Scoring and invalid-choice retry |
| `tests/test_cli.py` | Main-menu and invalid saved-data CLI behaviour |

## Shared API contracts

- Ticket functions take the shared `tickets` list explicitly; no module relies on a hidden global ticket collection.
- `create_ticket(tickets, title, category, urgency, affected_users)` returns the created ticket or raises `ValueError`. It validates before appending.
- `assign_staff(tickets, ticket_id, staff_name)` returns the updated ticket or raises `ValueError`. The prior behaviour is preserved: assigning an open ticket also moves it to `in_progress`.
- `update_status(tickets, ticket_id, new_status)` allows only `open -> in_progress -> resolved` and `resolved -> open`. A rejected operation leaves ticket data unchanged.
- `add_note(tickets, ticket_id, author, message)` returns the new note or raises `ValueError`. The collection is an explicit first argument to match the existing function-based project style; it is not a global variable.
- `search_tickets(tickets, query, category, status, priority)` returns a result list and does not mutate ticket records.
- `generate_report(tickets)` returns a dictionary with `total`, `by_status`, `by_priority`, `by_category`, `unresolved`, `resolved`, and `resolution_percentage`.
- `load_tickets(path)` returns a new fully validated list or raises an error. Callers should replace their active collection only after the call succeeds.
- Invalid business operations use `ValueError`; file access failures use `OSError`. The CLI catches these and prints an actionable message.

## Branch and PR recommendations

Use real issue IDs from the shared repository. A possible naming scheme is `feat/<issue>-validation-and-notes` for A and `feat/<issue>-search-and-insights` for B. Avoid editing the same file on both branches unless both engineers explicitly coordinate. Because `main.py` imports the agreed APIs, B can build the menus against these contracts while A works on the business/data layer.

Each engineer should author a substantial PR, write at least five meaningful tests, inspect the partner's diff, leave at least two concrete review observations or questions, run relevant tests, address blocking feedback, and record approval before merge. After merging either PR, synchronize branches and run:

```bash
python -m unittest discover -s tests -v
```
