from mailing import MailClient
import sys
import os
creds= None

help_msg = """PyMail, simple tool for SMTP mailing sending using gmail

pymail [To] [Subject] [Content]

--interface -i  - opens command line interface
"""

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

if "--help" in sys.argv:
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
    if "--interface" in sys.argv or "-i" in sys.argv:
        m = MailClient(creds, config)
        while start:
            try:
                clear()
                print(f"\33[3mLogged as {m.credentials.login}, {m.get_number_of_mails()}\33[0m")
                print("- NEW MAIL 0\n- SHOW FAVORITES 1\n- ADD TO FAVORITES 2\n- REMOVE FROM FAVORITES 3\n- INBOX 4\n- EXIT 9")
                inp = input(">>> ")
                match inp.upper():
                    case "0" | "NEW MAIL":
                        m.send_mail()
                    case "1" | "SHOW FAVORITES":
                        m.show_favorites()
                    case "2" | "ADD TO FAVORITES":
                        m.add_to_favorites()
                    case "3" | "REMOVE FROM FAVORITES":
                        m.remove_from_favorites()
                    case "4" | "INBOX":
                        m.show_inbox()
                    case "9":
                        break
                    case _:
                        print("Not supported input")
                        m.press_enter()
                clear()
            except (KeyboardInterrupt, EOFError):
                break
    else:
        m = MailClient(creds, config, silent=True)
        msg = m._setup_message(sys.argv[1], sys.argv[2], sys.argv[3])
        m._send_mail(msg)

