# CampusFlow Next design decisions

## 1. Preserve the existing function-and-dictionary approach

The project remains a small CLI built on Python functions, lists, dictionaries, JSON, exceptions, and `unittest`. It introduces no third-party packages, databases, web frameworks, or service infrastructure.

## 2. Validate before mutation

Input and state checks happen before a ticket or note is modified. Tests take a copy of the initial state and compare it after a rejected operation. The CLI's `_perform_and_save` helper also restores the in-memory list if a valid change cannot be persisted.

## 3. Share field rules

`validation.py` defines canonical category, urgency, priority, status, title, number, staff-label, and note rules. Ticket creation, workflow operations, search filters, and storage use these helpers rather than copying slightly different rules into menus.

## 4. Keep ticket IDs and note IDs independent

Ticket IDs use `T001`, `T002`, etc. Notes use a separate sequence for each ticket: `N001`, `N002`, etc. The next ID is based on the highest numeric suffix, not the number of records, so gaps do not lead to collisions.

## 5. Maintain old JSON list format and support old tickets

The JSON file remains a list of ticket dictionaries, like the previous project. The first version did not have `notes`; when such a record is loaded, the loader copies it and supplies `notes: []` in memory. It does not rewrite the file merely by loading it. Other invalid data is rejected rather than silently repaired.

## 6. Validate a complete load before use

JSON parsing is only syntax checking. After decoding, the loader checks required fields and types, allowed values, positive affected-user counts, unique ticket IDs, priority consistency, statuses, note shapes, message length, and per-ticket note ID uniqueness. It returns the new list only after all records pass, so the caller can retain existing memory on failure.

## 7. Save by temporary file then replace

The save function validates data first, serializes to a temporary file in the target directory, flushes the file, and then replaces the target. This prevents invalid data or a serialization failure from truncating the existing save file.

## 8. Preserve the Open Work Queue contract

The required Open Work Queue contains only `open` tickets. It sorts by priority order and numeric ticket ID, and it doesn't reorder the stored collection. The compatibility function `get_unresolved_queue` delegates to the same open-only behaviour even though its old name is less precise.

## 9. Search is read-only and combined filters use AND

Title matching is a case-insensitive substring comparison using `casefold()`. Optional category, status, and priority filters all need to match when supplied. Search results are a new list; sorting search results returns another list.

## 10. Reports reflect current state

Reopened tickets count as open because the report reads current status. Unresolved means open plus in-progress. When total tickets is zero, the resolution percentage is explicitly 0 instead of dividing by zero.

## 11. CLI and business logic are separate

The CLI reads and displays values. The business/data functions enforce validity and state rules, allowing direct unit tests that don't have to navigate menus. Engineer B's note menus call Engineer A's `add_note` and `get_ticket_notes` APIs.

## 12. Baseline and learning records are evidence, not fiction

The baseline and AI-learning documents are templates until the team performs the relevant work. Record actual commands, results, experiments, and decisions; do not claim to have reproduced an old bug or verified an AI recommendation without evidence.
