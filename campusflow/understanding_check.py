"""Engineer B's interactive Engineering Understanding Check.

The question bank is separate from both answer collection and scoring so the
scoring rules can be unit-tested without running a full CLI session.
"""


QUESTION_BANK = [
    {
        "question": "T001 is open and unassigned. A user tries to move it to in_progress. What should happen?",
        "choices": {
            "A": "Accept the change",
            "B": "Reject and preserve all data",
            "C": "Resolve the ticket automatically",
            "D": "Remove the ticket",
        },
        "answer": "B",
    },
    {
        "question": "The app has zero tickets. What should resolution percentage display?",
        "choices": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "answer": "C",
    },
    {
        "question": "Title='wifi', category='Network', status='open'. Which records should match?",
        "choices": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "answer": "B",
    },
    {
        "question": "A resolved ticket receives 'Add note'. What should happen?",
        "choices": {
            "A": "Append the note anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "answer": "C",
    },
    {
        "question": "The JSON file includes two tickets with the same ID. What should load do?",
        "choices": {
            "A": "Keep both tickets",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "answer": "C",
    },
    {
        "question": "A PR changes validation but has no negative-case tests. What is the best review action?",
        "choices": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "answer": "B",
    },
]


def score_answers(answers, questions=None):
    """Return the number of correct submitted choices (maximum six by default)."""
    question_bank = QUESTION_BANK if questions is None else questions
    score = 0
    for index, question in enumerate(question_bank):
        if index >= len(answers):
            continue
        submitted = answers[index]
        if isinstance(submitted, str) and submitted.strip().upper() == question["answer"]:
            score += 1
    return score


def run_understanding_check():
    """Run the six-question quiz, retry invalid options, and request two explanations."""
    print("\nENGINEERING UNDERSTANDING CHECK")
    print("Choose A, B, C, or D for each question.\n")

    answers = []
    for number, question in enumerate(QUESTION_BANK, start=1):
        print(f"Q{number}. {question['question']}")
        for letter, choice in question["choices"].items():
            print(f"  {letter}. {choice}")

        while True:
            answer = input("Your answer (A/B/C/D): ").strip().upper()
            if answer in ("A", "B", "C", "D"):
                answers.append(answer)
                break
            print("Invalid choice. Please enter A, B, C, or D.")
        print()

    score = score_answers(answers)
    print(f"Final score: {score}/{len(QUESTION_BANK)}")
    print("\nMentor discussion: briefly explain at least two of your answers.")
    explanations = []
    for number in (1, 2):
        explanation = input(f"Your explanation for Q{number}: ").strip()
        if not explanation:
            explanation = "No explanation provided."
        explanations.append((number, explanation))

    print("\nExplanations for mentor discussion:")
    for number, explanation in explanations:
        print(f"Q{number}: {explanation}")
    return score
