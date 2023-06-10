from collections import UserDict, UserList
from collections.abc import Iterator
from typing import Any, Generator
from datetime import datetime
import re

UKR_MOBILE_PHONE_CODES = [
    '095',
    '099',
    '050',
    '063',
    '066',
    '067',
    '077',
    '0800',
    '045',
    '046',
    '032',
    '044',
    '048',
    '068',
    '097',
    '098',
    '091',
    '092',
    '094',
]


class PhoneWrongFormat(Exception):
    def __init__(self, number: str) -> None:
        self.message = (
            f'Wrong format {number} \n'
            f'\tAll phone numbers should be added'
            f'according to a phone pattern:'
            '+code of a country(XX)XXXXXXX or 0XXXXXXXXX'
        )
        super().__init__(self.message)


class PhoneExsits(Exception):
    def __init__(self, number: str) -> None:
        self.message = f'Phone {number} exsits'
        super().__init__(self.message)


class ContactNotExsits(Exception):
    def __init__(self, name: str) -> None:
        self.message = f'Contact {name} not exsits'
        super().__init__(self.message)


class PhoneNotExsits(Exception):
    def __init__(self, number: str) -> None:
        self.message = f'Phone {number} not exsits'
        super().__init__(self.message)


class BirthdayWrongFormat(Exception):
    def __init__(self, date) -> None:
        self.message = f'Format {date} wrong'
        super().__init__(self.message)


class BirthdayWrongData(Exception):
    def __init__(self, date) -> None:
        self.message = f'Birhtdate  {date} not valide'
        super().__init__(self.message)



class Field:
    def __init__(self, value: Any) -> None:
        _value = self.check_value(value)
        self.value = _value

    @property
    def value(self) -> Any:
        return self.__value

    @value.setter
    def value(self, value: Any) -> None:
        self.__value = value

    def check_value(self, value: Any) -> Any:
        return value

    def __str__(self) -> str:
        return self.value


class Name(Field):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Phone(UserList):
    def __init__(self, number: str | int) -> None:
        UserList.__init__(self)
        number = self._check_number(number)
        self.append(number)

    def _sanitizer_number(self, number: str) -> str:
        return re.sub('[+\-() ]', '', number)

    def _validate_number(self, number: str) -> bool:
        return bool(re.fullmatch(r'^([0-9]){6,14}[0-9]$', number))

    def _check_number(self, number: str | int) -> str:
        if isinstance(number, int):
            number = str(number)

        _number = self._sanitizer_number(number)
        if self._validate_number(_number):
            for inner_code in UKR_MOBILE_PHONE_CODES:
                if _number.startswith(inner_code):
                    return f'38{_number}'
            return _number
        raise PhoneWrongFormat(number)

    @property
    def get(self) -> list[str]:
        return self.data

    def add_phone_num(self, number: str | int) -> None:
        _number = self._check_number(number)
        self.append(_number)

    def __str__(self) -> str:
        return f'Info: telephone number(-s): {", ".join(self.data)}'


class Email(Field):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return f'Email: {super().__str__()}'


class Birthday(Field):
    def __init__(self, date: tuple[int, int, int]) -> None:
        super().__init__(date)

    def check_value(self, date_b: tuple[int, int, int]) -> datetime:
        if len(date_b) != 3:
            raise BirthdayWrongFormat(date_b)

        year, month, day = date_b
        if not (
            year < datetime.now().year and 1 <= month <= 12 and 1 <= day <= 31
        ):
            raise BirthdayWrongData(date_b)
        return datetime(year, month, day)

    def _replace(self, year: int) -> datetime:
        try:
            return self.value.replace(year=year)
        except ValueError:
            return self.value.replace(year=year, day=28)

    def diff_day(self) -> int:
        current_date = datetime.now()
        birthday = self._replace(year=current_date.year)
        diff = (birthday - current_date).days

        if diff < 0:
            birthday: datetime = self._replace(year=current_date.year + 1)
            diff = (birthday - current_date).days

        return diff

    def __str__(self) -> str:
        self.value: datetime
        return f"Birthday: {self.value.strftime('Day:%d Month:%m Year:%Y')}"


class Record:
    def __init__(
        self,
        name: str,
        phone: str | int | None = None,
        email: str | None = None,
        date_b: tuple | None = None,
    ) -> None:
        self.name = Name(name)

        self.phone = None
        self.email = None
        self.birth_day = None

        if phone is not None:
            self.phone = Phone(phone)

        if email is not None:
            self.email = Email(email)

        if date_b is not None:
            self.birth_day = Birthday(date_b)

    def add_number(self, phone: str | int) -> None:
        if self.phone is not None:
            self.phone.add_phone_num(phone)
        else:
            self.phone = Phone(phone)

    def delete_number(self, phone_num) -> None:
        if self.phone is not None:
            self.phone.remove(phone_num)
        # raise not init phone

    def change_number(self, old_phone_num, changed_phone_num) -> None:
        if self.phone is not None:
            try:
                ind = self.phone.index(old_phone_num)
            except ValueError:
                raise PhoneNotExsits(old_phone_num)
            self.phone.remove(old_phone_num)
            self.phone.insert(ind, changed_phone_num)

    def add_change_email(self, email_val) -> None:
        self.email = Email(email_val)

    def add_bd(self, date: tuple) -> None:
        self.birth_day = Birthday(date)

    def days_to_birthday_(self) -> int | None:
        if self.birth_day:
            return self.birth_day.diff_day()
        # raise not init Birthday

    def __str__(self) -> str:
        birth_day = self.birth_day or 'Birthday: Empty'
        email = self.email or 'Email: Empty'
        phones = self.phone or 'Phones: Empty'
        return (
            f'Name: {self.name} -> {phones} | {email} | {birth_day}.'
        )


class AddressBook(UserDict):
    N: int = 2

    def __getitem__(self, key: str) -> Record:
        return super().__getitem__(key)

    def __iter__(self) -> Iterator:
        return iter(self.data.values())

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def add_phone_number(self, name: str, number: str) -> None:
        if name not in self.data:
            raise ContactNotExsits(name)
        self.data[name].add_number(number)

    def delete_record(self, name: str) -> None:
        if name not in self.data:
            raise ContactNotExsits(name)
        del self.data[name]

    @property
    def __str__(self) -> str:
        return '\n'.join(map(str, self.data.values()))

    def iterator(self) -> Generator[Record, None, None]:
        start = 0
        end = self.N
        while True:
            data = list(self.data.keys())[start:end]
            if not data:
                break
            for name in data:
                yield self.data[name]
            start = end
            end += self.N


def main():
    contacts = AddressBook()
    record1 = Record('name1')
    contacts.add_record(record1)
    for rec in contacts:
        print(rec)

    record1.add_number('0500905666')
    print('-' * 80)

    record2 = Record('name2')
    record2.add_number('380997778899')
    contacts.add_record(record2)
    for rec in contacts:
        print(rec)

    record1.add_number(44090123456)
    record2.add_change_email('some_email')
    for rec in contacts:
        print(rec)

    print(contacts['name1'].phone)
    try:
        contacts['name2'].add_number(333)
    except PhoneWrongFormat as exp:
        print(exp.message)
    for rec in contacts:
        print(rec)

    try:
        contacts.add_record(Record('name3', 3131, 'another_email', (1993, 12, 22)))
    except PhoneWrongFormat as exp:
        print(exp.message)

    for rec in contacts:
        print(rec)

    # print(contacts['name3'].email)
    try:
        contacts['name2'].change_number('+380(99)7778899', '+380(99)7778090')
    except PhoneNotExsits as exp:
        print(exp.message)
    for rec in contacts:
        print(rec)

    # print(contacts['name3'].days_to_birthday_())
    contacts.add_record(
        Record('name4', '0800123456', 'email@gmail.com', (1992, 3, 4))
    )
    contacts['name1'].add_bd((1999, 6, 22))
    for rec in contacts:
        print(rec)
    print('days_diff', contacts['name4'].days_to_birthday_())
    print(contacts['name1'].birth_day)
    print(
        contacts['name1'].phone,
        contacts['name1'].email,
        contacts['name2'].name,
    )
    contacts['name1'].add_bd((1999, 7, 22))
    res = contacts.iterator()

    for i in res:
        print('-' * 80)
        print(i)

if __name__ == '__main__':
    main()
