from prompt_toolkit import PromptSession
from typeahead import Typeahead
from decorator import input_error
from addressBook import AddressBook
from contactRecord import Record
import pickle


commands = {
        "hello": "Greet the user",
        "close": "Exit the application",
        "exit": "Exit the application",
        "add_contact": "Add a contact",
        "change_contact": "Modify a contact",
        "phone": "Show the contact's phone number",
        "all_contacts": "Show all contacts",
        "add_birthday": "Add a birthday to a contact",
        "show_birthday": "Show a contact's birthday",
        "upcoming_birthdays": "Show upcoming birthdays",
        "help": "Show all commands",
        "search_contact": "Search for a contact",

        
        "delete_contact": "Delete a contact",
        "add_note": "Add a note",
        "edit_note": "Edit a note",
        "delete_note": "Delete a note",
        "search_notes": "Search for a note",
        "all_notes": "Show all notes",
        # "add_tag": "Add a tag to a note",
        # "remove_tag": "Remove a note's tag",
    }

@input_error
def search_contact(args, book: AddressBook):
    name = args[0]
    record: Record = book.find(name.title())
    if record is None:
        return f"There is no such contact in your book"
    else:
        return f"Here is what you have in your book -> {str(record)}"


@input_error
def add_contact(args, book: AddressBook):
    """
    Add new contact to the dictionary
    2 and only 2 args expected: Name and phone number, separated by space
    All names are stored from capital
    """
    name, phone, *_ = args
    record = book.find(name.title())
    message = "Contact updated"
    if record is None:
        record = Record(name.title())
        book.add_record(record)
        message = "Contact added"
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    """
    Updates number for already existing contact.
    requires name and phone number.
    """
    name, old_phone, new_phone, *_ = args
    record: Record = book.find(name.title())
    
    if record is not None:
        if new_phone.isdigit() and len(new_phone) == 10:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated"
        else:
            return "New number must has 10 digits"
    else:
        return "There is no such Contact in your book" 

@input_error
def show_phone(args, book: AddressBook):
    """
    Shows phone number if requested contact exists.
    requires name, that matches with available in contacts.
    """
    name = args[0]
    record: Record = book.find(name.title())
    if record is not None:
        if len(record.phones) > 0:
            phones = []
            for phone_recording in record.phones:
                phones.append(phone_recording.value)
            return f"Available phone(s) for {record.name.value}:\n {phones}"
        else:
            return f"{name.title()} doesn't have any phones yet"
    else:
        return f"There is no {name.title()} in your book, please add it first"

def show_all(book: AddressBook):
    """
    Shows all contacts and their numbers saved during session
    """
    if not book:
        return "No contacts found"
    
    output_lines = []
    for name, record in book.data.items():
        output_lines.append(str(record))
    
    return "\n".join(output_lines)

@input_error
def add_birthday(args, book: AddressBook):
    """
    Adding birthday to existing contact
    """
    name, birthday_date_string, *_ = args
    record: Record = book.find(name.title())
    # Note: creating Birthday object here just for validation, 
    # then passing string to record which creates it again. 
    # Simplified to just passing string, Record handles validation inside Birthday init.
    if record:
        record.add_birthday(birthday_date_string)
        return f"Birthday for {record.name} was successfully updated"
    else:
        return "Contact not found"

@input_error
def show_birthday(args, book: AddressBook):
    """
    Showing birthday if existing Contact exists.
    """
    name, *_ = args
    record: Record = book.find(name.title())
    if record is not None:
        if record.birthday is not None:
            return f"The birthday date of {record.name.value.title()} is {record.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return f"There is no set birthday date for {name.title()}"
    else:
        return f"There is no {name.title()} in your book, please add it first"
    
def birthdays(book: AddressBook):
    """
    Shows congratulation list for the contacts in the book that needs to be congratulated.
    """
    if not book:
        return "No contacts found in your book"
    else:
        return book.get_upcoming_birthdays()

def parse_input(user_input):
    """
    Divides input to commands and arguments.
    """
    cleaned_input = user_input.strip()
    if not cleaned_input:
        return None, [] 

    parts = cleaned_input.split()
    cmd = parts[0].lower()
    args = parts[1:]
    
    return cmd, args

def show_help(commands_list):
    """Display help with all commands, parameters, and descriptions."""
    print("\n" + "=" * 70)
    print("📚 Personal Assistant - Available Commands")
    print("=" * 70)
    for key,value in commands.items():
        print(f"Command '{key}': {value}")
    print("=" * 70)




    # print("\n📞 Contact Management:")
    # for cmd in Command.Contacts:
    #     help_info = COMMAND_HELP[cmd]
    #     print(help_info.format(cmd.value, width=45))

    # print("\n📝 Note Management:")
    # for cmd in Command.Notes:
    #     help_info = COMMAND_HELP[cmd]
    #     print(help_info.format(cmd.value, width=45))

    # print("\n⚙️ General:")
    # for cmd in Command.General:
    #     help_info = COMMAND_HELP[cmd]
    #     print(help_info.format(cmd.value, width=45))

    # print("\n" + "=" * 70)
    # print("Legend:")
    # print("  <parameter>  Required parameter")
    # print("  [parameter]  Optional parameter")
    # print("=" * 70 + "\n")

# --- Functions for saving and loading ---

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Returning empty addressBook if file not found

# --- MAIN ---

def main():
    # load data on start
    book = load_data()
    session = PromptSession()
    completer = Typeahead(hints=commands.keys())
    print("Welcome to the assistant bot!")
    show_help(commands)

    while True:
        
        user_input = session.prompt('Enter a command: ', completer=completer)
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # Saving before exiting
            save_data(book)
            print("Good bye!")
            break
        
        elif command == "hello":
            print("How can I help you?")
            
        elif command == "add_contact":
            print(add_contact(args, book))
            
        elif command == "change_contact":
            print(change_contact(args, book))
            
        elif command == "phone":
            print(show_phone(args, book))
        
        elif command == "all_contacts":
            print(show_all(book))
            
        elif command == "add_birthday":
            print(add_birthday(args, book))

        elif command == "show_birthday":
            print(show_birthday(args, book))

        elif command == "upcoming_birthdays":
            result = birthdays(book)
            if isinstance(result, list):
                print("Congratulations list for next seven days:")
                for contact in result:
                    print(contact)
            else:
                print(result)
        elif command == "help":
            show_help(commands)
        elif command == "search_contact":
            print(search_contact(args, book))
            
        elif command is None:
            continue

        else:
            print("Invalid command.")

# if __name__ == "__main__":
main()