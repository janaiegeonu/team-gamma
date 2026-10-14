# Bug-hunter challenge notes

The assignment asks each engineer to choose one edge case for the partner's module, explain the initial state and input, compare expected and actual outcomes, and record any fix. The tests below are included as candidate scenarios; during real peer review, each engineer should run the partner's branch and fill in the reviewer's actual observations rather than claiming an unobserved defect.

## Engineer A reviewing Engineer B's search module

- Test name: `test_casefold_handles_unicode_case_expansion`
- Initial state: one valid open ticket whose title is `Straße network issue`.
- Input: title query `STRASSE`.
- Expected: the ticket is returned because the requirement specifically uses `casefold()` for caseless substring comparison.
- Actual result in this reference implementation: test passes; one matching ticket is returned.
- Defect reproduced before a fix: `Not yet established; run against the teammate's branch and record the actual result.`
- Code change made due to review: `Fill in after review. Do not claim a fix unless one was made.`

## Engineer B reviewing Engineer A's Open Work Queue

- Test name: `test_numeric_ticket_id_tie_break_does_not_sort_t010_before_t002`
- Initial state: ten open tickets, all with the same low priority and IDs `T001` through `T010`.
- Input: request the Open Work Queue.
- Expected: tickets remain in numeric ID order, so `T002` appears before `T010`.
- Actual result in this reference implementation: test passes; IDs appear in numeric order.
- Defect reproduced before a fix: `Not yet established; run against the teammate's branch and record the actual result.`
- Code change made due to review: `Fill in after review. Do not claim a fix unless one was made.`

## Reciprocal review evidence

After the two engineers exchange PRs, replace the placeholders above with the real branch/commit, observed result, review comment, and any correction. If the partner's version already passes, record that no defect was reproduced and no fix was necessary. A passing test should not be presented as a bug that was found and fixed.
