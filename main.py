import sys

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker


from models import User
from commands import commands, def_mod

engine = create_engine("sqlite:///book.db")
Session = sessionmaker(bind=engine)
session = Session()


def confirm(question):
    """Use it when user makes important changes to the AddressBook, for example deleting a contact"""
    while True:
        string = input(question)
        if string.strip().lower() in ("y", "yes"):
            return True
        if string.strip().lower() in ("n", "no"):
            return False


if __name__ == "__main__":
    current_user_id = 1
    user = session.query(User).filter_by(id=current_user_id).first()
    login = user.login if user else None
    if login is None:
        user = User(login="TestUser", password="test")
        session.add(user)
        session.commit()
    print("\nWelcome to your personal Python assistant!")
    has_account = confirm("Do you have an account? yes/no\n")
    if not has_account:
        new_account = confirm("Do you want to create a new account? yes/no\n")
        if not new_account:
            print("Using testing account")
        else:
            login = ""
            while not login:
                login = input("Please enter your login:\n")
                user = session.query(User).filter_by(login=login).first()
                if user is not None:
                    user_id = user.id
                    print(f"user {login} already exists")
                    login = ""
            password = ""
            # while not password:
            #     password = input("Please enter your password:\n")
            user = User(login=login, password=password)
            session.add(user)
            session.commit()
            current_user_id = user.id
    else:
        login = ""
        while not login:
            login = input("Please enter your login:\n")
            user = session.query(User).filter_by(login=login).first()
            # print(user.login)
            if user is None:
                print(f"user '{login}' does not exist")
                login = ''
        current_user_id = user.id
    print(f"Hello, {login}! What can I do for you today?")

    while True:
        command = input()
        mode, data = def_mod(command)
        output = commands.get(mode)(session, current_user_id, data)
        if output != '':
            print(output)
        if output == "Good bye!":
            sys.exit()
