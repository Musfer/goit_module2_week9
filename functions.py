import re
from datetime import datetime

import sqlalchemy.orm
import models
import show_info
import inspect
import types


phone_pattern = "\s\+?[-\s]?(?:\d{2,3})?[-\s]?(?:\([-\s]?\d{2,3}[-\s]?\)|\d{2,3})?[-\s]?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3}\s"
no_number = "Sorry, I can't identify a phone number."
no_name = "Sorry, I can't identify a contact's name."


# def find_name_number(text: str):
#     """splits text into phone number and name"""
#     text += " "
#     pattern = re.compile(phone_pattern)
#     only_name = text
#     if not pattern.findall(text):
#         return find_name(text), ""
#     for x in pattern.findall(text):
#         only_name = only_name[:only_name.find(x)]
#     return find_name(only_name), str(pattern.findall(text)[0]).strip().replace(" ", "").replace("", ""),


def find_name(text: str):
    """converts sting into a valid name of contact"""
    return text.strip().lower().title()


def empty(*_):
    """called if an empty command is passed to assistant.
    works differently if the assistant is in the show records mode.
    shouldn't be decorated ny decorator to work properly"""
    return ""


def add_contact(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<add contact 'name' -- creates a new contact>help1
        add contact from 'text' to your AddressBook"""
    name = find_name(data)
    if not name:
        return no_name
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    contacts = [x.fullname for x in contacts]
    if name in contacts:
        return f"Contact '{name}' already exists"
    else:
        contact = models.Contact(fullname=name, user_id=user_id)
        session.add(contact)
        session.commit()
        return f"Created contact a new contact '{name}'"


def find(session: sqlalchemy.orm.Session, user_id: int, data: str):
    data = data.strip()
    result = ""

    contacts = session.query(models.Contact).filter_by(user_id=user_id).filter(
        models.Contact.fullname.like(f"%{data}%")).all()
    # print([x for x in contacts])
    if contacts:
        result += "In contacts:\n"
        for x in contacts:
            result += show_contact(session, user_id, x.fullname) + "\n"
        result += "\n"

    emails = session.query(models.Email).filter(models.Email.mail.like(f"%{data}%")).all()
    contacts = set()
    for email in emails:
        x = session.query(models.Contact).filter_by(user_id=user_id).filter_by(id=email.contact_id).first()
        if x:
            contacts.add(x)
    if contacts:
        result += "In emails:\n"
        for x in contacts:
            result += show_contact(session, user_id, x.fullname) + "\n"
        result += "\n"

    phones = session.query(models.Phone).filter(models.Phone.number.like(f"%{data}%")).all()
    contacts = set()
    for phone in phones:
        x = session.query(models.Contact).filter_by(user_id=user_id).filter_by(id=phone.contact_id).first()
        if x:
            contacts.add(x)
    if contacts:
        result += "In phone numbers:\n"
        for x in contacts:
            result += show_contact(session, user_id, x.fullname) + "\n"
        result += "\n"
    return result if result else "No matches found"


def delete_contact(session: sqlalchemy.orm.Session, user_id: int, data: str):
    name = find_name(data)
    if not name:
        return no_name
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    known_contacts = [x.fullname for x in contacts]
    for contact in known_contacts:
        if contact.lower() in name.lower():
            contact_with_name = session.query(models.Contact).filter_by(fullname=contact, user_id=user_id).first()
            session.delete(contact_with_name)
            session.commit()
            return "done"


def delete_email(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<delete email 'name' 'email' -- deletes an email from the contact>help2
    deletes one email"""
    name, email = name_email(session, user_id, data)
    if not name:
        return "Can't find an existing contact name"
    if not email:
        return "Can't find an email"
    contact_id = session.query(models.Contact).filter_by(user_id=user_id, fullname=name).first().id
    mails = session.query(models.Email).filter_by(contact_id=contact_id)
    for x in mails:
        if x.mail == email:
            print(x.mail)
            session.delete(x)
            session.commit()
            return f"Delted email address {email} from contact {name}"
    return f"Contact {name} doesn't have email address {email}"


def delete_number(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<delete number 'name' 'phone number' -- deletes the 'phone number' from the contact>help2
    deletes a number of contact from 'data'"""
    name, number = name_number(session, user_id, data)
    if not name:
        return "Can't find an existing contact name"
    if not number:
        return "Can't find a valod phone number"
    contact_id = session.query(models.Contact).filter_by(user_id=user_id, fullname=name).first().id
    phone = session.query(models.Phone).filter_by(contact_id=contact_id, number=number).first()
    try:
        session.delete(phone)
        session.commit()
        return f"Delted phone number {number} from contact {name}"
    except Exception as err:
        pass
    return f"Contact {name} doesn't have phone number {number}"


def delete_birthday(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<delete birthday 'name' -- deletes birthdays of the contact>help2
    clears a birthday field of the contact from 'data'"""
    name = find_name(data)
    if not name:
        return no_name
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    known_contacts = [x.fullname for x in contacts]
    for contact in known_contacts:
        if contact.lower() in name.lower():
            contact_with_name = session.query(models.Contact).filter_by(fullname=contact, user_id=user_id).first()
            contact_with_name.date_of_birth = None
            session.commit()
            return "done"


def add_number(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<add phone 'name' 'valid phone number' -- adds a new phone number to the contact>help1
    adds a number from 'text' to an existing contact from 'text'"""
    name, number = name_number(session, user_id, data)
    if not name:
        return no_name
    elif not number:
        return no_number
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    contacts = [x.fullname for x in contacts]
    if name not in contacts:
        return f"Contact '{name}' does not exists"
    else:
        try:
            contact_id = session.query(models.Contact).filter_by(fullname=name, user_id=user_id).first().id
            phone = models.Phone(number=number, contact_id=contact_id)
            session.add(phone)
            session.commit()
            return f"Number '{number}' has been added to contact '{name}'"
        except Exception as err:
            return err


def show_contact(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<show contact 'name' -- shows a contact with name 'name'>help0
    shows a contact by its name"""
    name = find_name(data)
    if not name:
        return "Sorry, I can't identify a contact's name"
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    contacts = [x.fullname for x in contacts]
    if name not in contacts:
        return f"Contact '{name}' is not in your contacts"
    else:
        contact_id = session.query(models.Contact).filter_by(fullname=name, user_id=user_id).first().id
        contact_reader = show_info.ShowContact(session, contact_id)
        return contact_reader.show()


def show_all(session: sqlalchemy.orm.Session, user_id: int, *_):
    """help<show all -- shows all contacts with name >help0
    shows a contact by its name"""
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    contacts = [x.fullname for x in contacts]
    result = ""
    for contact in contacts:
        result += show_contact(session, user_id, contact) + "\n"
    return result if result else "Your book is empty"


def name_email(session, user_id: int, text: str):
    """splits 'text' into name and email"""
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    known_contacts = [x.fullname for x in contacts]
    # known_contacts = query.list_of_contacts(user_id)
    for contact in known_contacts:
        if contact.lower() in text.lower():
            template = re.compile(r"[a-zA-Z][a-zA-Z0-9_.]+@[a-zA-Z]+\.[a-zA-Z][a-zA-Z]+")
            mails = text.lower().replace(contact.lower(), "", 1).strip()
            mail_list = re.findall(template, mails)
            if mail_list and mail_list[0]:
                return contact, mail_list[0]
            else:
                return contact, None
    return None, None


def name_number(session, user_id: int, text: str):
    """splits 'text' into name and email"""
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    known_contacts = [x.fullname for x in contacts]
    name = ""
    for contact in known_contacts:
        if contact.lower() in text.lower():
            name = contact
            template = re.compile(phone_pattern)
            text = text.lower().replace(contact.lower(), "", 1).strip()

            phone_list = template.findall(" "+text+" ")
            if phone_list and phone_list[0]:
                phone = phone_list[0].strip()
                return contact, phone
    return name, None


def add_email(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<add email 'name' 'email' -- ands a new email to the contact>help1
        adds email to the existing contact"""
    name, email = name_email(session, user_id, data)
    if name is None:
        return "Can't find a valid contact"
    if email is None:
        return "Can't find a valid email address"
    contact_id = session.query(models.Contact).filter_by(fullname=name, user_id=user_id).first().id
    email = models.Email(mail=email, contact_id=contact_id)
    session.add(email)
    session.commit()
    return "Done"


def name_birthday(session, user_id: int, text: str):
    """splits 'text' into contact name and a date"""
    contacts = session.query(models.Contact).filter_by(user_id=user_id)
    known_contacts = [x.fullname for x in contacts]
    for contact in known_contacts:
        if contact.lower() in text.lower():
            return contact, text.lower().replace(contact.lower(), "", 1).strip()
    return None, None


def convert_to_date(birthday: str = None):
    birthday_date = None
    try:
        birthday_date = datetime.strptime(birthday, '%m.%d.%Y')
    except ValueError:
        pass
    try:
        birthday_date = datetime.strptime(birthday, '%m.%d')
        birthday_date = birthday_date.replace(year=2)
    except ValueError:
        pass
    try:
        birthday = birthday.replace("29", "28", 1)
        birthday_date = datetime.strptime(birthday, '%m.%d.%Y')
    except:
        pass
    return birthday_date


def set_birthday(session: sqlalchemy.orm.Session, user_id: int, data: str):
    """help<set birthday 'name' 'valid date' -- changes a birthday of the contact>help3
    changes or sets a birthday of the contact"""
    name, birthday = name_birthday(session, user_id, data)
    if name is None:
        return no_name
    if birthday is None:
        "No date specified"
    date = convert_to_date(birthday)
    if date is None:
        return "Invalid date use mm.dd.yyyy or mm.dd format"
    else:
        contact_id = session.query(models.Contact).filter_by(fullname=name).first().id
        contact = (session.query(models.Contact).filter_by(id=contact_id).first())
        contact.date_of_birth = date
        session.commit()
        return "Done"


def help_me(*_):
    """help<'valid phone number' should be 7 digits long + optional 3 digits of city code + optional 2 digits of country code + optional '+' sign
    \t'birthday' should be in forman 'mm.dd' or 'mm.dd.year'
    \t'email' name1.name2@domen1.domen2, should have at least one name and two domain names>help9
    """
    commands = dir(__import__(inspect.getmodulename(__file__)))  # all objects in module
    functions = list(filter(lambda x: (isinstance(eval(x), types.FunctionType)), commands))  # only functions

    def help_line(func_name: str):  # returns info for help function from func_name function
        pattern = r"help<([\s\S]+)>help(\d)"
        function = eval(func_name)
        if function.__doc__:
            doc = function.__doc__
        else:
            return None
        m = re.findall(pattern, doc)
        if m:
            message, priority = m[0]
            return message, priority
        else:
            return None

    help_list = []
    for func in functions:
        line = help_line(func)
        if line:
            help_list.append(line)

    helper = show_info.Helper(help_list)
    return helper.show()
