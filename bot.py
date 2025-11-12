import functools
import pickle
from collections import UserDict
from datetime import datetime, timedelta, date

class Field:
    def __init__(self, value):
        self.__value = value.strip()

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        try:
            formatted_string = '%d.%m.%Y'
            self.value = datetime.strptime(value, formatted_string).date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY format for real calendar dates")

class Phone(Field):
    def __init__(self, value):
        if isinstance(value, str) and value.isdigit() and len(value) == 10:
            self.value = value
        else:
            raise ValueError("Phone number must be a 10-digit string")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birhday_string):
        self.birthday = Birthday(birhday_string)

    def show_birthday(self):
        return self.birthday

    def add_phone(self, phone_number):
        phone_num_act = Phone(phone_number)
        self.phones.append(phone_num_act)
    
    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj

    def edit_phone(self, old_phone, new_phone):
        phone_obj_to_edit = self.find_phone(old_phone)
        if phone_obj_to_edit:
            phone_obj_to_edit.value = new_phone
        else:
            raise ValueError(f"Phone number '{old_phone}' not found for editing within '{self.name}' record")
    
    def remove_phone(self, phone_num):
        phone_obj_to_remove = self.find_phone(phone_num)
        if phone_obj_to_remove:
            self.phones.remove(phone_obj_to_remove)
        else:
            raise ValueError(f"Phone number '{phone_num}' not found in record for {self.name}.")

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        if self.birthday is not None:
            return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        if isinstance(record, Record):
            self.data[record.name.value] = record
        else:
            raise TypeError("Only Record objects can be added to AddressBook.")
        
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact '{name}' not found in the address book.")
    
    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming_birthdays = []
        try:
            for name, record in self.data.items():
                if record.birthday is not None:
                    # Replace year with the current year
                    birthday_this_year = record.birthday.value.replace(year=today.year)

                    # If birthday already passed this year, use next year
                    if birthday_this_year < today:
                        birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                    # If birthday is on weekend, move to next Monday
                    if birthday_this_year.weekday() == 5:  # Saturday
                        birthday_this_year += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:  # Sunday
                        birthday_this_year += timedelta(days=1)
                    
                    # Check if the (possibly shifted) date is within the next 7 days
                    if 0 <= (birthday_this_year - today).days <= 7:
                        upcoming_birthdays.append({
                            "name": name,
                            "original_birthday": record.birthday.value.strftime("%d.%m.%Y"),
                            "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
                        })
                
            if len(upcoming_birthdays) == 0:
                return 'There is no one to congratulate in next 7 days'
            else:
                sorted_upcoming_birthdays = sorted(upcoming_birthdays, key=lambda x: x['congratulation_date'])
                return sorted_upcoming_birthdays  
        except ValueError:
            raise ValueError(f"Wrong incoming data, please check your adressbook")

def input_error(func):
    """
    Decorator for caching user's input errors like KeyError, ValueError, IndexError
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Wrong parameters are provided, please try again with valid data"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter user name."
    return inner

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
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # Saving before exiting
            save_data(book)
            print("Good bye!")
            break
        
        elif command == "hello":
            print("How can I help you?")
            
        elif command == "add":
            print(add_contact(args, book))
            
        elif command == "change":
            print(change_contact(args, book))
            
        elif command == "phone":
            print(show_phone(args, book))
        
        elif command == "all":
            print(show_all(book))
            
        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            result = birthdays(book)
            if isinstance(result, list):
                print("Congratulations list for next seven days:")
                for contact in result:
                    print(contact)
            else:
                print(result)
            
        elif command is None:
            continue

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()