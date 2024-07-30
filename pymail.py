from mailing import MailClient
import sys
import os
from tabulate import tabulate
creds= None

help_msg = """PyMail, simple tool for SMTP mailing sending using gmail

pymail [To] [Subject] [Content]

--interface  -i  - opens command line interface
             -f  - use recipient from favorites
--list-favorites - list all favorites
--silent         - mailing client does not print anything execpt errors, works only for headless

example:
    pymail -fdarling "I will be later" "Hello my darling!\n\nI will be home little later\nWith Love\nM"
    pymail some@mail.com "Test mail" "This is a test." --silent

    pymail -i < opens Command Line Interface 
"""
is_silent = not "--silent" in sys.argv

def clear():
    os.system("cls" if os.name=="nt" else "clear")

class Credentials:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __str__(self):
        return f"{self.login}, ******"
    def __repr__(self):
        return f"{self.login}, ******"


# read credentials
try:
    with open(f"/{os.getenv('HOME')}/.pymail.conf", "r") as f:
        ff = f.read().split(",")
        creds = Credentials(ff[0], ff[1])
    start = True
except FileNotFoundError:
    print("\33[38;1;41mCould not locate 'credentials.creds'! Create such file under /home/{user}/.pymail.conf and insert your credentials in this way: 'my@mail.com,Password1'\33[0m")
    start = False

if "--help" in sys.argv or len(sys.argv) == 1:
    print(help_msg)
    start = False


if start:
    config = {
            "smtp":{
                "server": "smtp.gmail.com",
                "port":587,
                "timeout": 120
            },
            "pop3":{
                "host": "pop.gmail.com",
                "port":995
                }
            }
    # CLI
    if "--interface" in sys.argv or "-i" in sys.argv:
        m = MailClient(creds, config)
        while start:
            try:
                clear()
                print(f"\33[3mLogged as {m.credentials.login}, Inbox: {m.get_number_of_mails()}\33[0m")
                print("- NEW MAIL 0\n- SHOW FAVORITES 1\n- ADD TO FAVORITES 2\n- REMOVE FROM FAVORITES 3\n- INBOX 4\n- EXIT 9")
                inp = input(">>> ")
                match inp.upper():
                    case "0" | "NEW" | "NEW MAIL":
                        m.send_mail()
                    case "1" | "SHOW FAVORITES":
                        m.show_favorites()
                    case "2" | "ADD TO FAVORITES":
                        m.add_to_favorites()
                    case "3" | "REMOVE FROM FAVORITES":
                        m.remove_from_favorites()
                    case "4" | "INBOX":
                        m.show_inbox()
                    case "9" | "EXIT":
                        break
                    case _:
                        print("Not supported input")
                        m.press_enter()
                clear()
            except (KeyboardInterrupt, EOFError):
                break
    # list facorites
    elif "--list-favorites" in sys.argv:
        m = MailClient(creds, config, initialize_smtp=False, initialize_pop3=False, silent=is_silent)
        data = m._fetch_all_favorites()
        print(tabulate(data, headers="keys"))
    # headless
    else:
        m = MailClient(creds, config, silent=is_silent, initialize_pop3=False)
        try:
            # set to
            if sys.argv[1].startswith("-f"):
                recipient = m._fetch_from_favorites(sys.argv[1][2:])
            else:
                recipient = sys.argv[1]
            msg = m._setup_message(to=recipient, subject=sys.argv[2], content=sys.argv[3])
            m._send_mail(msg)
        except IndexError:
            print("Some arguments are missing! use --help!")

