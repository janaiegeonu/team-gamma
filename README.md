# CampusFlow Next

CampusFlow Next is an updated Python command-line helpdesk application. It keeps the original ticket workflow and priority rules while adding safer validation and JSON persistence, structured follow-up notes, combined search filters, richer reports, automated tests, and an Engineering Understanding Check.

## Requirements

- Python 3.9 or newer
- Python standard library only; no third-party packages are required

## Run the application

From the project root:

```bash
python main.py
```

The application stores tickets in `data/tickets.json`. If that file does not exist, CampusFlow starts with an empty collection and creates the folder/file when a successful change is saved. **When applying these changes to your existing repository, keep your existing `data/tickets.json`; do not replace it with an empty sample file.** Older records without a `notes` field are loaded with `notes: []` in memory. They are not rewritten just by loading.

## Run the tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests use `unittest`, temporary directories, and the standard library. They do not require a real ticket file or campus information.

## Main features

- Create tickets with canonical category and urgency values.
- Calculate priority using the original rule precedence: critical for high urgency **and** at least 10 affected users; otherwise high for high urgency **or** at least 10 users; otherwise medium for medium urgency **or** at least 3 users; otherwise low.
- Assign staff and enforce the original `open -> in_progress -> resolved` workflow plus `resolved -> open` reopening. As in the previous application, assigning an open ticket also starts it.
- Show the original Open Work Queue with **only open tickets**, sorted by priority (`critical`, `high`, `medium`, `low`) and then numeric ticket ID.
- Add and view structured follow-up notes. Notes are allowed on open and in-progress tickets only; each ticket has its own `N001`, `N002`, ... sequence.
- Search titles by case-insensitive substring and combine optional category, status, and priority filters using logical AND.
- Optionally sort search results by priority and numeric ticket ID.
- Report totals, counts by status/priority/category, unresolved and resolved counts, and resolution percentage. Empty data reports 0%.
- Validate loaded JSON before returning it to the application; reject duplicate IDs, invalid ticket/note fields, illegal statuses, and priority inconsistencies.
- Write saves through a temporary file and replace the target only after serialization succeeds.
- Run the six-question Engineering Understanding Check.

## JSON data shape

The saved file remains a JSON **list** of ticket dictionaries, matching the original project's envelope. Each ticket contains:

```json
{
  "id": "T001",
  "title": "Wi-Fi not working",
  "category": "Network",
  "urgency": "high",
  "affected_users": 15,
  "priority": "critical",
  "status": "open",
  "assigned_to": null,
  "notes": []
}
```

Each note is a dictionary with `note_id`, `author`, and `message`. Note IDs are unique within a ticket, so `T001/N001` and `T002/N001` are different note identities.

## Engineering ownership and merge boundaries

See [`docs/engineer-ownership.md`](docs/engineer-ownership.md) for the proposed Engineer A / Engineer B split and agreed interfaces, [`docs/acceptance-test-map.md`](docs/acceptance-test-map.md) for requirement-to-test coverage, and [`docs/bug-hunter-tests.md`](docs/bug-hunter-tests.md) for reciprocal edge-case review ideas. Keep changes to the files assigned to each engineer as much as possible to reduce merge conflicts. Both engineers should review and test each other's pull requests, then rerun the full test suite after integration.

## Documentation still requiring your real project evidence

- [`docs/baseline-check.md`](docs/baseline-check.md) is a template. Run the old audited commit and record the actual results before you claim a baseline.
- [`docs/ai-learning-log.md`](docs/ai-learning-log.md) is a template. Fill it with the questions you actually asked, experiments you actually ran, and evidence you actually checked. Do not invent learning cycles.
- [`docs/design-decisions.md`](docs/design-decisions.md) describes the important implementation choices and compatibility behaviour.

## Important integration note

This is an updated reference project built from the supplied source and assignment requirements. Before replacing files in your live team repository, commit or back up the current branch, compare the diff, and preserve the real `data/tickets.json`. Verify the audited baseline separately; the tests in this updated project cannot establish how the previous commit behaved.
