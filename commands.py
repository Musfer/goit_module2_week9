# from functions import add_contact, show_all, add_number, help_me, delete_number, delete_contact, set_birthday
# from functions import show_contact, empty, reset, delete_birthday, find, save_to_file, read_from_file, clear
# from functions import add_email, delete_email, find_birthdays, rename, create_note, delete_note, edit_note
# from functions import show_all_notes, show_note_list, show_note

from functions import add_contact, empty, show_contact, add_number, help_me, add_email, set_birthday, delete_contact
from functions import show_all, delete_birthday, delete_email, delete_number, find


commands = {
    "hello": lambda *_: "How can I help you?",
    "bye": lambda *_: "Good bye!",
    "add_contact": add_contact,
    "empty": empty,
    "show": show_contact,
    "add_number": add_number,
    "help_me": help_me,
    "add_email": add_email,
    "set_birthday": set_birthday,
    "delete_contact": delete_contact,
    "show_all": show_all,
    "delete_birthday": delete_birthday,
    "find": find,
    "delete_email": delete_email,
    "delete_number": delete_number,


    # "rename": rename,
    # "reset": reset,
    # "save": save_to_file,
    # "load": read_from_file,
    # "clear": clear,
    # "show_birthday": find_birthdays,

    # "create_note": create_note,
    # "delete_note": delete_note,
    # "edit_note": edit_note,
    # "show_all_notes": show_all_notes,
    # "show_note_list": show_note_list,
    # "show_note": show_note,
    0: lambda *_: "Sorry I can't understand you. Try 'help' command to see what I can.",
}


def def_mod(string: str):
    try:
        mods = {
            # ".": "exit",
            "hello": "hello",
            "good bye": "bye",
            "close": "bye",
            "exit": "bye",
            "add contact": "add_contact",
            "add number": "add_number",
            "add email": "add_email",
            "find": "find",
            "delete contact": "delete_contact",
            "delete number": "delete_number",
            # "delete birthday": "delete_birthday",
            "show contact": "show",
            "show all": "show_all",
            "set birthday": "set_birthday",
            "help": "help_me",
            "delete email": "delete_email",
            # "show birthday": "show_birthday",
            "rename": "rename",
            # "create note": "create_note",
            # "delete note": "delete_note",
            # "edit note": "edit_note",
            # "show notes": "show_all_notes",
            # "show note list": "show_note_list",
            # "show note": "show_note"
        }
        if not string:
            return "empty", ""
        for key_word in mods.keys():
            if key_word in string.lower():
                return mods[key_word], string.replace(key_word, "", 1)
        return 0, ""
    except Exception as err:
        return err
