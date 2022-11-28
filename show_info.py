from abc import abstractmethod, ABC
import query
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm
import models
from datetime import datetime


class IRepr(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def show(self):  # generates a string with info about contact from record
        pass


class Helper(IRepr):
    def __init__(self, commands: list):
        self.commands = commands

    def show(self):
        sorted_commands = sorted(self.commands, key=(lambda x: x[1]))
        sorted_strings = [x[0] for x in sorted_commands]
        return "\t"+"\n\t".join(sorted_strings)


class ShowContact(IRepr):
    def __init__(self, session: sqlalchemy.orm.Session, record_id: int):
        self.record_id = record_id
        self.session = session

    def show(self):
        if self.record_id is None:
            return ""
        string = ""
        contact = (self.session.query(models.Contact).filter_by(id=self.record_id).first())
        string += f"{contact.fullname}:"
        numbers = (self.session.query(models.Phone).filter_by(contact_id=self.record_id))
        string += f"\n\tPhone numbers: {', '.join([x.number for x in numbers]) if numbers  else 'empty'}"
        emails = (self.session.query(models.Email).filter_by(contact_id=self.record_id))
        string += f"\n\tMails: {', '.join([x.mail for x in emails]) if emails  else 'empty'}"
        birthday = contact.date_of_birth
        string += f"\n\tBirthday: {birthday.strftime('%B %d') if birthday else ''}"
        return string


# class ShowContacts(IRepr):
#     def __init__(self, book: classes.AddressBook, n: int):
#         self.book = book
#         self.n = n  # contacts per page
#
#     def show(self):
#         if not self.book.data:
#             return "Your phone book is empty."
#         else:
#             first = self.book.page * self.n + 1  # first contact to show
#             last = min(self.book.page * self.n + self.n, self.book.size)  # last contact to show
#             if self.book.size == last:
#                 pass
#             zero_line = f"Showing contacts {first}-{last} from {self.book.size} records:\n"
#             if not self.book.showing_records:
#                 self.book.showing_records = True
#                 self.book.reset_iterator(self.n)
#             try:
#                 contacts_to_show = next(self.book.show)  # list of names of next contacts to show
#                 output_line = zero_line
#                 for name in contacts_to_show:
#                     record_reader = ShowRecord(self.book.data.get(name))
#                     output_line += record_reader.show()
#                 if last == self.book.size:
#                     output_line += f"End of the address book"
#                     self.book.page = 0
#                 else:
#                     output_line += f"Press 'Enter' to show next {self.n} contacts"
#                     self.book.page += 1
#                 return output_line
#             except StopIteration:
#                 self.book.showing_records = False
#                 self.book.reset_iterator(self.n)
#                 self.book.page = 0
#                 return ""
#


