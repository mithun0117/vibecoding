"""
Library Management System
===========================
A menu-driven console application using dictionaries to store book data.

Features:
    - Add Book
    - Issue Book
    - Return Book
    - Search Book
    - Display Books

Each book is stored as a dictionary entry keyed by a unique Book ID:

    books = {
        "B001": {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "copies_total": 3,
            "copies_available": 2,
            "issued_to": ["Alice"],
        },
        ...
    }
"""

# --------------------------------------------------------------------------
# In-memory data store
# --------------------------------------------------------------------------

books = {}  # Book ID -> book details dictionary


# --------------------------------------------------------------------------
# Custom exceptions for clear, specific error handling
# --------------------------------------------------------------------------

class LibraryError(Exception):
    """Base class for all expected library errors."""
    pass


class BookNotFoundError(LibraryError):
    pass


class DuplicateBookError(LibraryError):
    pass


class NoCopiesAvailableError(LibraryError):
    pass


class NotIssuedError(LibraryError):
    """Raised when trying to return a book that was never issued to that person."""
    pass


# --------------------------------------------------------------------------
# Input validation helpers
# --------------------------------------------------------------------------

def prompt_nonempty(message):
    """Repeat the prompt until a non-empty string is entered."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("  This field cannot be empty. Please try again.")


def prompt_positive_int(message):
    """Repeat the prompt until a positive integer is entered."""
    while True:
        raw = input(message).strip()
        try:
            value = int(raw)
            if value <= 0:
                print("  Please enter a whole number greater than zero.")
                continue
            return value
        except ValueError:
            print("  Please enter a valid whole number.")


def prompt_menu_choice(valid_choices, message="\nSelect an option: "):
    """Repeat the prompt until one of the valid menu choices is entered."""
    while True:
        choice = input(message).strip()
        if choice in valid_choices:
            return choice
        print(f"  Invalid choice. Please enter one of: {', '.join(valid_choices)}")


# --------------------------------------------------------------------------
# Core library operations
# --------------------------------------------------------------------------

def add_book(book_id, title, author, copies):
    """
    Add a new book to the catalog.
    Raises DuplicateBookError if the book ID already exists.
    """
    if book_id in books:
        raise DuplicateBookError(f"A book with ID '{book_id}' already exists.")

    books[book_id] = {
        "title": title,
        "author": author,
        "copies_total": copies,
        "copies_available": copies,
        "issued_to": [],
    }


def issue_book(book_id, borrower_name):
    """
    Issue a book to a borrower, decrementing available copies.
    Raises BookNotFoundError or NoCopiesAvailableError as appropriate.
    """
    if book_id not in books:
        raise BookNotFoundError(f"No book found with ID '{book_id}'.")

    book = books[book_id]
    if book["copies_available"] <= 0:
        raise NoCopiesAvailableError(
            f"'{book['title']}' has no copies available right now."
        )

    book["copies_available"] -= 1
    book["issued_to"].append(borrower_name)


def return_book(book_id, borrower_name):
    """
    Return a book previously issued to a borrower, incrementing available copies.
    Raises BookNotFoundError or NotIssuedError as appropriate.
    """
    if book_id not in books:
        raise BookNotFoundError(f"No book found with ID '{book_id}'.")

    book = books[book_id]
    if borrower_name not in book["issued_to"]:
        raise NotIssuedError(
            f"No record of '{borrower_name}' having borrowed '{book['title']}'."
        )

    book["issued_to"].remove(borrower_name)
    book["copies_available"] += 1


def search_books(keyword):
    """
    Search the catalog by title or author (case-insensitive, partial match).
    Returns a dict of matching {book_id: book} entries.
    """
    keyword = keyword.lower()
    return {
        book_id: book
        for book_id, book in books.items()
        if keyword in book["title"].lower() or keyword in book["author"].lower()
    }


# --------------------------------------------------------------------------
# Formatted display helpers
# --------------------------------------------------------------------------

def print_header(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def print_book_row(book_id, book):
    issued_display = ", ".join(book["issued_to"]) if book["issued_to"] else "-"
    print(
        f"{book_id:<8}{book['title'][:22]:<24}{book['author'][:16]:<18}"
        f"{book['copies_available']}/{book['copies_total']:<6}{issued_display}"
    )


def print_books_table(book_dict):
    if not book_dict:
        print("No books to display.")
        return
    print(f"{'ID':<8}{'Title':<24}{'Author':<18}{'Avail':<9}{'Issued To'}")
    print("-" * 60)
    for book_id, book in book_dict.items():
        print_book_row(book_id, book)


# --------------------------------------------------------------------------
# Menu actions (handle user interaction + call core functions)
# --------------------------------------------------------------------------

def action_add_book():
    print_header("Add Book")
    try:
        book_id = prompt_nonempty("Book ID (e.g. B001): ").upper()
        title = prompt_nonempty("Title: ")
        author = prompt_nonempty("Author: ")
        copies = prompt_positive_int("Number of copies: ")

        add_book(book_id, title, author, copies)
        print(f"\n'{title}' added successfully with {copies} copy/copies.")
    except DuplicateBookError as e:
        print(f"\nError: {e}")
    except LibraryError as e:
        # Catch-all for any other expected library errors
        print(f"\nError: {e}")


def action_issue_book():
    print_header("Issue Book")
    try:
        book_id = prompt_nonempty("Book ID: ").upper()
        borrower = prompt_nonempty("Borrower's name: ")

        issue_book(book_id, borrower)
        print(f"\n'{books[book_id]['title']}' issued to {borrower}.")
    except (BookNotFoundError, NoCopiesAvailableError) as e:
        print(f"\nError: {e}")


def action_return_book():
    print_header("Return Book")
    try:
        book_id = prompt_nonempty("Book ID: ").upper()
        borrower = prompt_nonempty("Borrower's name: ")

        return_book(book_id, borrower)
        print(f"\n'{books[book_id]['title']}' returned by {borrower}.")
    except (BookNotFoundError, NotIssuedError) as e:
        print(f"\nError: {e}")


def action_search_book():
    print_header("Search Book")
    keyword = prompt_nonempty("Enter title or author keyword: ")
    results = search_books(keyword)
    print(f"\n{len(results)} result(s) found:\n")
    print_books_table(results)


def action_display_books():
    print_header("All Books")
    print_books_table(books)


# --------------------------------------------------------------------------
# Main menu loop
# --------------------------------------------------------------------------

MENU = """
1. Add Book
2. Issue Book
3. Return Book
4. Search Book
5. Display Books
6. Exit
"""

MENU_ACTIONS = {
    "1": action_add_book,
    "2": action_issue_book,
    "3": action_return_book,
    "4": action_search_book,
    "5": action_display_books,
}


def main():
    print_header("LIBRARY MANAGEMENT SYSTEM")

    while True:
        print(MENU)
        choice = prompt_menu_choice(valid_choices=["1", "2", "3", "4", "5", "6"])

        if choice == "6":
            print("\nGoodbye!")
            break

        try:
            MENU_ACTIONS[choice]()
        except Exception as e:
            # Safety net for any unexpected error so the program never crashes
            print(f"\nAn unexpected error occurred: {e}")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
