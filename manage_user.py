from models import db, User
import bcrypt
import readline


# global variables that contains several types of commands
create_commands = [ "create", "create_user", "createuser", "adduser", "add" ]
update_commands = [ "update", "update_user", "updateuser", "passwd" ]
delete_commands = [ "delete", "delete_user", "deluser", "del" ]
list_commands = [ "list", "list_users", "listusers", "ls" ]
help_commands = [ "help", "?" ]
exit_commands = [ "quit", "exit", "bye" ]

commands = create_commands + update_commands + delete_commands + list_commands + help_commands + exit_commands

# the prompt or the ps1 variable (reference to the $PS1 variable of a shell in *NIX)
ps4 = "pef_db $ "


def completer(text,state):
    cmds = [c for c in commands if c.startswith(text)]
    try:
        return cmds[state]
    except IndexError:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def process_command(command:str):
    """
    Process the commands that the user enters
    """
    try:
        # we parse the command
        command = command.split()
        if command[0] in create_commands:
            create_user(command[1], command[2])
        elif command[0] in update_commands:
            update_user(command[1])
        elif command[0] in delete_commands:
            delete_user(command[1])
        elif command[0] in list_commands:
            try:
                if command[1] in ["-v","--verbose"]:
                    list_users(True)
                else:
                    print("No valid argument passed going to default")
                    list_users()
            except IndexError:
                list_users()
        elif command[0] in help_commands:
            usage()
        elif command[0] in exit_commands:
            quit()
        else:
            print("No valid command entered type ? or help to find more informations")
    except IndexError:
        print("")


def create_user(name:str, password):
    """
    Create a user with a given username and password in the database
    :param str name: the username
    :param str password: the password
    """
    if User.query.get(name):
        print(f"Sorry the user '{name}' already exists in database, please consider using another name")
    else:
        u = User(name,bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()))
        print(f"\nNew User:\nName = {u.name}\nPassword = {password}\nIs that correct ? [Y/n]")
        if input(">> ") in ['', 'Y', 'y', 'yes']:
            db.session.add(u)
            db.session.commit()
            print(f"User {u.name} added")
    print("")


def update_user(name:str):
    """
    Change the password of a user, it updates the user password in the database
    :param str name: the name of the user we want to change the password
    """
    if User.query.get(name):
        u = User.query.get(name)
        new_pass = input(f"Enter a new password for the user '{name}': ")
        new_pass_confirm = input("Confirm the new password: ")

        if new_pass == new_pass_confirm:
            u.password = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
            db.session.commit()
            print(f"Password for user '{name}' have been changed successfully")
        else:
            print("Passwords don't match\nCancelling password update")
    else:
        print(f"Cannot find the user '{name}'")
    print("")


def delete_user(name:str):
    """
    Delete a user from database
    :param str name: the name of teh user we want to delete
    """
    if not User.query.get(name):
        print(f"Sorry the user '{name}' cannot be found")
    else:
        u = User.query.get(name)
        print(f"\nDeleting user:\nName = {u.name}\nAre you sure ? [Y/n]")
        if input(">> ") in ['', 'Y', 'y', 'yes']:
            db.session.delete(u)
            db.session.commit()
            print(f"User {u.name} deleted")
    print("")


def list_users(complete=False):
    """
    Give a list of all the users stored in the database
    :param boolean complete: whether the output of the command should be verbose or not
    """
    users = User.query.all()
    if len(users) == 0:
        print("No users in database yet")
    else:
        if not complete:
            for user in users:
                print(user.name)
        else:
            for user in users:
                print(f"{user.name} : {user.password}")
    print("")

def usage():
    """
    Shows how to use the cli
    """
    print("Here is a list of available commands:")
    print("     create / createuser / create_user / adduser / add [username] [password] : Add a new user in the database")
    print("     update / updateuser / update_user / passwd [username]                   : Change the password of the user $username")
    print("     delete / deleteuser / delete_user / deluser / del [username]            : Delete the user $username from the database")
    print("     list / list_users / ls [-v, --verbose]                                  : lists all the users in the database")
    print("     help / ?                                                                : show this help screen")
    print("     quit / bye / exit                                                       : Exits the program\n")

def quit():
    """
    Quit the cli properly
    """
    print("Bye!\n")
    exit()


# main loop, keyboardInterrupt behaves like the quit() command
while True:
    try:
        command = input(ps4)
        process_command(command)
    except KeyboardInterrupt:
        quit()
