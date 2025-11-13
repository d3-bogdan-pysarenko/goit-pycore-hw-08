from datetime import datetime

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
