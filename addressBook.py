from collections import UserDict
from datetime import timedelta, date
from contactRecord import Record

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
