"""Main CLI entry point for the CampusFlow Next helpdesk application.

Engineer B owns the CLI integration, search/report views, and understanding
check. Ticket rules and persistence remain in the campusflow package modules.
"""

from copy import deepcopy
from pathlib import Path

from campusflow.notes import add_note, get_ticket_notes
from campusflow.reports import generate_report
from campusflow.search import search_tickets, sort_search_results_by_priority
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.understanding_check import run_understanding_check
from campusflow.validation import (
    validate_category,
    validate_priority,
    validate_status,
    validate_urgency,
)
from campusflow.workflow import (
    assign_staff,
    find_ticket,
    get_open_work_queue,
    update_status,
)


# Saved tickets are stored inside the project's data folder.
DATA_FILE = Path(__file__).parent / "data" / "tickets.json"


def display_ticket(ticket):
    """Display the fields staff need when viewing one ticket."""
    print("-" * 48)
    print(f"Ticket ID:      {ticket['id']}")
    print(f"Title:          {ticket['title']}")
    print(f"Category:       {ticket['category']}")
    print(f"Urgency:        {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority:       {ticket['priority']}")
    print(f"Status:         {ticket['status']}")
    print(f"Assigned to:    {ticket['assigned_to'] or 'Not assigned'}")
    print(f"Notes:          {len(ticket.get('notes', []))}")
    print("-" * 48)


def _perform_and_save(tickets, operation):
    """Run a mutating action and restore memory if the action/save fails.

    The snapshot is deliberately simple: if persistence fails after a valid
    business change, the active list is restored so memory and disk do not
    silently disagree. ``operation`` is a small function for one action.
    """
    before = deepcopy(tickets)
    try:
        result = operation()
        save_tickets(tickets, DATA_FILE)
        return result
    except Exception:
        tickets[:] = before
        raise


def create_new_ticket(tickets):
    """Collect ticket input, create the ticket, and persist it safely."""
    while True:
        title = input("\nEnter ticket title: ").strip()
        if title:
            break
        print("Error: Ticket title cannot be empty. Please try again.")

    category_options = {
        "1": "Network",
        "2": "Hardware",
        "3": "Software",
        "4": "Other",
    }
    while True:
        print("\nChoose a category:")
        print("1. Network")
        print("2. Hardware")
        print("3. Software")
        print("4. Other")
        category_choice = input("Enter your choice (1-4): ").strip()
        if category_choice in category_options:
            category = category_options[category_choice]
            break
        print("Error: Invalid category. Choose an option from 1 to 4.")

    urgency_options = {"1": "low", "2": "medium", "3": "high"}
    while True:
        print("\nChoose urgency:")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        urgency_choice = input("Enter your choice (1-3): ").strip()
        if urgency_choice in urgency_options:
            urgency = urgency_options[urgency_choice]
            break
        print("Error: Invalid urgency. Choose an option from 1 to 3.")

    while True:
        raw_users = input("\nEnter the number of affected users: ").strip()
        try:
            affected_users = int(raw_users)
            if affected_users > 0:
                break
            print("Error: Affected users must be greater than zero.")
        except ValueError:
            print("Error: Enter a whole number, such as 5.")

    try:
        ticket = _perform_and_save(
            tickets,
            lambda: create_ticket(tickets, title, category, urgency, affected_users),
        )
        print(f"\nTicket {ticket['id']} created successfully!")
        display_ticket(ticket)
    except (ValueError, OSError) as error:
        print(f"\nError creating ticket: {error}")


def list_tickets(tickets):
    """Display all tickets in their collection order."""
    if not tickets:
        print("\nNo tickets found.")
        return
    print("\nALL TICKETS")
    for ticket in tickets:
        display_ticket(ticket)


def _tickets_by_priority(tickets):
    """Return a separately sorted list for assignment/status selection views."""
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(
        tickets,
        key=lambda ticket: (priority_order[ticket["priority"]], int(ticket["id"][1:])),
    )


def _display_ticket_choices(tickets):
    """Display compact ticket details in priority order."""
    for ticket in _tickets_by_priority(tickets):
        print(
            f"\nID: {ticket['id']} | Priority: {ticket['priority'].upper()} | "
            f"Status: {ticket['status']}"
        )
        print(f"Title: {ticket['title']}")
        print(f"Category: {ticket['category']}")
        print(f"Assigned to: {ticket['assigned_to'] or 'Not assigned'}")


def _ask_for_ticket(tickets, prompt, allow_resolved=True):
    """Ask for an existing ticket ID; entering 0 cancels the operation."""
    while True:
        ticket_id = input(prompt).strip()
        if ticket_id == "0":
            print("Operation cancelled.")
            return None
        try:
            ticket = find_ticket(tickets, ticket_id)
            if not allow_resolved and ticket["status"] == "resolved":
                print("Error: This ticket is resolved. Reopen it before modifying it.")
                continue
            return ticket
        except ValueError as error:
            print(f"Error: {error} Please enter an available ticket ID.")


def assign_ticket_to_staff(tickets):
    """Prompt for an assignment and save the approved change."""
    if not tickets:
        print("\nThere are no tickets to assign.")
        return

    print("\n========== ASSIGN STAFF ==========")
    _display_ticket_choices(tickets)
    ticket = _ask_for_ticket(
        tickets,
        "\nEnter ticket ID to assign staff (or 0 to cancel): ",
        allow_resolved=False,
    )
    if ticket is None:
        return

    while True:
        staff_name = input("Enter the staff member's name (or 0 to cancel): ").strip()
        if staff_name == "0":
            print("Staff assignment cancelled.")
            return
        if staff_name:
            break
        print("Error: Staff name cannot be empty. Please try again.")

    try:
        updated = _perform_and_save(
            tickets,
            lambda: assign_staff(tickets, ticket["id"], staff_name),
        )
        print(
            f"\nTicket {updated['id']} successfully assigned to "
            f"{updated['assigned_to']}. Status: {updated['status']}."
        )
    except (ValueError, OSError) as error:
        print(f"Error assigning staff: {error}")


def change_ticket_status(tickets):
    """Offer only sensible next status choices and rely on workflow validation."""
    if not tickets:
        print("\nThere are no tickets available to update.")
        return

    print("\n========== UPDATE TICKET STATUS ==========")
    _display_ticket_choices(tickets)
    ticket = _ask_for_ticket(
        tickets,
        "\nEnter ticket ID to update (or 0 to cancel): ",
    )
    if ticket is None:
        return

    options = {
        "open": {"1": "in_progress"},
        "in_progress": {"1": "resolved"},
        "resolved": {"1": "open"},
    }
    status_options = options[ticket["status"]]

    # Do not offer an action the selected ticket cannot currently take.
    if ticket["status"] == "open" and not ticket["assigned_to"]:
        print("This ticket is unassigned. Assign a staff member before starting work.")
        return

    while True:
        print("\nChoose the new status:")
        for number, status in status_options.items():
            print(f"{number}. {status.replace('_', ' ').title()}")
        print("0. Cancel")
        choice = input("Enter your choice: ").strip()
        if choice == "0":
            print("Status update cancelled.")
            return
        if choice not in status_options:
            print("Error: Invalid choice. Please try again.")
            continue

        try:
            updated = _perform_and_save(
                tickets,
                lambda: update_status(tickets, ticket["id"], status_options[choice]),
            )
            print(f"Ticket {updated['id']} status updated to {updated['status']}.")
            return
        except (ValueError, OSError) as error:
            print(f"Error updating status: {error}")
            return


def show_open_work_queue(tickets):
    """Display only open tickets, with higher priority first."""
    queue = get_open_work_queue(tickets)
    if not queue:
        print("\nThe Open Work Queue is empty.")
        return

    print("\nOPEN WORK QUEUE")
    print("Only open tickets are shown, ordered by priority and numeric ticket ID.")
    for ticket in queue:
        display_ticket(ticket)


def show_reports(tickets):
    """Display the complete ticket report and resolution insights."""
    report = generate_report(tickets)
    print("\nCAMPUSFLOW REPORT")
    print("=" * 34)
    print(f"Total tickets: {report['total']}")

    print("\nTickets by status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nTickets by priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")

    print("\nTickets by category:")
    for category, count in report["by_category"].items():
        print(f"  {category}: {count}")

    print(f"\nUnresolved tickets: {report['unresolved']}")
    print(f"Resolved tickets: {report['resolved']}")
    print(f"Resolution percentage: {report['resolution_percentage']:.1f}%")
    print("=" * 34)


def _ask_optional_filter(label, normalizer):
    """Ask for a filter; blank means no filter and invalid values are retried."""
    while True:
        value = input(f"{label} (leave blank for any): ").strip()
        if not value:
            return None
        try:
            return normalizer(value)
        except ValueError as error:
            print(f"Invalid filter: {error}")


def search_tickets_cli(tickets):
    """Collect combined search filters and display results without modifying data."""
    print("\nSEARCH TICKETS")
    query = input("Title contains (leave blank for any title): ").strip()
    category = _ask_optional_filter("Category: Network, Hardware, Software, Other", validate_category)
    status = _ask_optional_filter("Status: open, in_progress, resolved", validate_status)
    priority = _ask_optional_filter("Priority: critical, high, medium, low", validate_priority)

    try:
        results = search_tickets(
            tickets, query=query, category=category, status=status, priority=priority
        )
    except ValueError as error:
        print(f"Search could not be completed: {error}")
        return

    if not results:
        print("No tickets matched all supplied filters.")
        return

    while True:
        sort_choice = input("Sort these results by priority? (y/n): ").strip().lower()
        if sort_choice in ("y", "yes"):
            results = sort_search_results_by_priority(results)
            break
        if sort_choice in ("n", "no"):
            break
        print("Please enter y or n.")

    print(f"\n{len(results)} matching ticket(s):")
    for ticket in results:
        print(
            f"{ticket['id']} | {ticket['title']} | {ticket['category']} | "
            f"{ticket['priority']} | {ticket['status']} | "
            f"{ticket['assigned_to'] or 'Not assigned'}"
        )


def add_ticket_note_cli(tickets):
    """Collect note input and delegate all business validation to Engineer A's API."""
    if not tickets:
        print("\nThere are no tickets to add notes to.")
        return
    ticket = _ask_for_ticket(tickets, "Ticket ID for the follow-up note (or 0 to cancel): ")
    if ticket is None:
        return

    author = input("Author label: ")
    message = input("Follow-up message (5-300 characters): ")
    try:
        note = _perform_and_save(
            tickets,
            lambda: add_note(tickets, ticket["id"], author, message),
        )
        print(f"Note {note['note_id']} added to ticket {ticket['id']}.")
    except (ValueError, OSError) as error:
        print(f"Could not add note: {error}")


def view_ticket_notes_cli(tickets):
    """Display a ticket's notes in note-ID order."""
    if not tickets:
        print("\nThere are no tickets to view notes for.")
        return
    ticket = _ask_for_ticket(tickets, "Ticket ID to view notes (or 0 to cancel): ")
    if ticket is None:
        return

    try:
        notes = get_ticket_notes(tickets, ticket["id"])
    except ValueError as error:
        print(f"Could not view notes: {error}")
        return

    print(f"\nFOLLOW-UP NOTES FOR {ticket['id']}")
    if not notes:
        print("No follow-up notes have been recorded.")
        return
    for note in notes:
        print(f"{note['note_id']} | {note['author']}: {note['message']}")


def show_menu():
    """Display the main application menu."""
    print("\n========== CAMPUSFLOW NEXT ==========")
    print("1. Create a ticket")
    print("2. List all tickets")
    print("3. Assign staff")
    print("4. Update ticket status")
    print("5. Open Work Queue")
    print("6. View reports")
    print("7. Search tickets")
    print("8. Add follow-up note")
    print("9. View ticket notes")
    print("10. Engineering Understanding Check")
    print("11. Exit")
    print("=====================================")


def load_tickets_for_application():
    """Load validated records or stop without altering the source file."""
    try:
        return load_tickets(DATA_FILE)
    except ValueError as error:
        print(f"\nCould not load saved tickets: {error}")
        print("The saved file was not changed. Correct or restore the file, then retry.")
        return None


def main():
    """Load saved tickets and run the interactive CampusFlow menu."""
    try:
        tickets = load_tickets_for_application()
    except OSError as error:
        print(f"Could not access saved tickets: {error}")
        return

    if tickets is None:
        return

    print("Welcome to CampusFlow Next!")
    while True:
        show_menu()
        choice = input("Choose an option (1-11): ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)
            elif choice == "2":
                list_tickets(tickets)
            elif choice == "3":
                assign_ticket_to_staff(tickets)
            elif choice == "4":
                change_ticket_status(tickets)
            elif choice == "5":
                show_open_work_queue(tickets)
            elif choice == "6":
                show_reports(tickets)
            elif choice == "7":
                search_tickets_cli(tickets)
            elif choice == "8":
                add_ticket_note_cli(tickets)
            elif choice == "9":
                view_ticket_notes_cli(tickets)
            elif choice == "10":
                run_understanding_check()
            elif choice == "11":
                print("Thank you for using CampusFlow Next!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 11.")
        except (ValueError, OSError) as error:
            print(f"\nOperation failed: {error}")


if __name__ == "__main__":
    main()
