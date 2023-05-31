from collections import UserDict, UserList
from datetime import datetime
import re

european_codes = {'380': 'UA', '43': 'AT', '335': 'AL', '376': 'AD', '374': 'AM', '32': 'BE', '359': 'BG', '387': 'BA',
                  '385': 'HR', '357': 'CY', '420': 'CZ', '45': 'DK', '372': 'EE', '358': 'FI',
                  '33': 'FR', '298': 'FO', '995': 'GE', '350': 'GI', '49': 'DE', '30': 'GR', '36': 'HU', '353': 'IE',
                  '39': 'IT', '354': 'IS', '371': 'LV', '370': 'LT', '352': 'LU',
                  '356': 'MT', '31': 'NL', '423': 'LI', '389': 'MK', '373': 'MD', '377': 'MC', '382': 'ME', '47': 'NO',
                  '48': 'PL', '351': 'PT', '40': 'RO', '421': 'SK', '386': 'SI',
                  '34': 'ES', '46': 'SE', '378': 'SM', '381': 'RS', '41': 'CH', '90': 'TR', '44': 'GB', }

ukr_mobile_phone_codes = ['095', '099', '050', '063', '066', '067', '077', '0800', '045', '046', '032', '044', '048',
                          '068', '097', '098', '091', '092', '094', ]


class Field:
    def __init__(self, value):
        self.value = value

    def set_value(self, val):
        if val:
            self.value = val

    @property
    def get(self):
        return self.value


class Name(Field):
    pass


class Phone(Field, UserList):
    def __init__(self, value):
        Field.__init__(self, value)
        UserList.__init__(self)
        self.value = None
        self.check_number(value)
        if self.value:
            self.data.append(self.value)

    def check_number(self, number):
        try:
            if number:
                number = [re.sub('[+\-() ]', '', symbol) for symbol in str(number)]
                if re.match(r'^([0-9]){6,14}[0-9]$', ''.join(number)):
                    for code in european_codes:
                        if ''.join(number).startswith(code):
                            number = ''.join(number[len(code):])
                            self.value = f'+{code}({number[:2]}){number[2:]}'
                            return f'+{code}({number[:2]}){number[2:]}'
                    else:
                        for inner_code in ukr_mobile_phone_codes:
                            if ''.join(number).startswith(inner_code) and len(number) == 10:
                                number = ''.join(number[1:])
                                self.value = f'+380({number[:2]}){number[2:]}'
                                return f'+380({number[:2]}){number[2:]}'
                else:
                    print('All phone numbers should be added according to a phone pattern: '
                          '+code of a country(XX)XXXXXXX or 0XXXXXXXXX')
        except (ValueError, IndexError) as error:
            print(error)

    @property
    def get(self):
        return self.data

    def add_phone_num(self, phone_num):
        res = self.check_number(phone_num)
        if self.value and res:
            self.data.append(self.value)


class Email(Field):
    pass


class Birthday(Field):
    def __init__(self, date: tuple):
        super().__init__(date)
        self.value = None
        self.check_date(date)

    def check_date(self, date_b: tuple):
        try:
            if date_b:
                year, month, day = int(date_b[0]), int(date_b[1]), int(date_b[2])
                if year in range(1900, datetime.now().year + 1) and month in range(1, 13) and day in range(1, 32):
                    self.value = datetime(year=date_b[0], month=date_b[1], day=date_b[2])
                else:
                    raise ValueError
        except (TypeError, ValueError, IndexError):
            print('A date of the birth has to be written according to a birthday pattern: YYYY, MM, DD')


class Record:
    def __init__(self, name: str, phone: str | int = None, email: str = None, date_b: tuple = ()):
        self.name = Name(name)
        self.phone = Phone(phone)
        self.email = Email(email)
        self.birth_day = Birthday(date_b)

    def add_number(self, phone: str | int):
        self.phone.add_phone_num(phone)

    def delete_number(self, phone_num):
        self.phone.remove(phone_num)

    def change_number(self, old_phone_num, changed_phone_num):
        ind = self.phone.index(old_phone_num)
        self.phone.remove(old_phone_num)
        self.phone.insert(ind, changed_phone_num)

    def add_change_email(self, email_val):
        self.email = Email(email_val)

    def add_bd(self, date: tuple):
        self.birth_day = Birthday(date)

    def days_to_birthday_(self):
        if self.birth_day.value:
            current_date: datetime = datetime.now()
            birthday: datetime = datetime(year=current_date.year, month=self.birth_day.value.month,
                                          day=self.birth_day.value.day)
            diff: int = (birthday - current_date).days
            if diff < 0:
                birthday = datetime(year=current_date.year + 1, month=self.birth_day.value.month,
                                    day=self.birth_day.value.day)
                diff = (birthday - current_date).days
            return diff

    '''def days_to_birthday__(self):
        if self.birth_day.value:
            return (datetime(year=datetime.now().year + 1, month=self.birth_day.value.month,
                             day=self.birth_day.value.day) - datetime.now()).days \
                if (datetime(year=datetime.now().year, month=self.birth_day.value.month,
                             day=self.birth_day.value.day) - datetime.now()).days < 0 \
                else (datetime(year=datetime.now().year, month=self.birth_day.value.month,
                               day=self.birth_day.value.day) - datetime.now()).days'''


class AddressBook(UserDict):
    N: int = 2

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete_record(self, name: str):
        del self.data[name]

    @property
    def __str__(self):
        return [f'Name: {name} -> Info: telephone number(-s): {rec.phone} | Email: {rec.email.get} '
                f'| Birthday: {rec.birth_day.get}.' for name, rec in self.data.items()]

    def iterator(self):
        start = 0
        end = self.N
        while True:
            data = list(self.data.keys())[start:end]
            if not data:
                break
            yield {name: f'Info: telephone number(-s): {self.data[name].phone} | Email: {self.data[name].email.get} '
                         f'| Birthday: {self.data[name].birth_day.get}.' for name in data}
            start = end
            end += self.N


# ----------------------------------------------------------------------------------------------------------------------
contacts = AddressBook()
record1 = Record('name1')
contacts.add_record(record1)
[print(rec) for rec in contacts.__str__]
print()
record1.add_number('0500905666')
print('-' * 222)
record2 = Record('name2')
record2.add_number('380997778899')
contacts.add_record(record2)
[print(rec) for rec in contacts.__str__]
print()
record1.add_number(44090123456)
record2.add_change_email('some_email')
[print(rec) for rec in contacts.__str__]
print()
print(contacts['name1'].phone)
contacts['name2'].phone.add_phone_num(333)
[print(rec) for rec in contacts.__str__]
print()
contacts.add_record(Record('name3', 3131, 'another_email', (1993, 12, 22)))
[print(rec) for rec in contacts.__str__]
print()
print(contacts['name3'].email.value)
contacts['name2'].change_number('+380(99)7778899', '+380(99)7778090')
[print(rec) for rec in contacts.__str__]
print()
print(contacts['name3'].days_to_birthday_())
contacts.add_record(Record('name4', '0800123456', 'email@gmail.com', (1992, 3, 4)))
contacts['name1'].add_bd((1999, 6, 22))
[print(rec) for rec in contacts.__str__]
print(contacts['name4'].days_to_birthday_())
print(contacts['name1'].birth_day.get)
print(contacts['name1'].phone.get, contacts['name1'].email.get, contacts['name2'].name.get)
contacts['name1'].add_bd((1999, 7, 22))
res = contacts.iterator()
for i in res:
    print('-' * 222)
    print(i)
    # input('Press any key.')
