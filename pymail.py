from mailing import MailClient, clear, Credentials, Style
from config import Config
import sys
import json
from getpass import getpass
import keyring

help_msg = """PyMail, mail client that uses SMTP and IMAP

On first startup, config creation interface will be open, it can be re-run using --reset-config argument
If one or more configs are missing or are invalid, config creation interface will be opened.

--cli          -i - opens command line interface
--command         - use command line interface
--update-password - opens password-update interface
--where-is-config - prints where config file is stored
--test            - run self-tests
--reset-config    - resets config and opens config setup

== COMMAND LINE Specific
pymail [To] [Subject] [Content]
             -f   - use recipient from favorites
             -o   - read contents from file
--list-favorites  - list all favorites
--silent          - mailing client does not print anything execpt errors, works only for headless

             -c [content-type] - message content type, if not provided, 'plain' is used 
             -d [directory]    - config file directory
--password   -p [password]     - provide password inline

examples:
    pymail -fdarling "I will be later" "Hello my darling!\\n\\nI will be home little later\\nWith Love\\nM"
    pymail some@mail.com "Test mail" "This is a test." --silent
    pymail some@mail.com "Html test" "<h1>Hello</h1><br>This is <b>HTML message</b>" -c html 
    pymail some@mail.com "password from file" "Password from file" -p "$(cat /home/someuser/pymail_password.txt)"
    pymail some@mail.com "config from file" "Config from file" -d /home/user/custom_pymail_config.conf 

    pymail -i < opens Command Line Interface 
"""
is_silent = not "--silent" in sys.argv


if "-d" in sys.argv:
    cf = Config(custom_directory=sys.argv[sys.argv.index("-d")+1])
elif "--reset-config" in sys.argv:
    cf = Config(reset_config=True)
else:
    cf = Config()

start = True


if "--help" in sys.argv or "-h" in sys.argv:
    print(help_msg)
    start = False

if "--where-is-config" in sys.argv:
    print(cf.config_path)
    start = False

if "--update-password" in sys.argv:
    new_password = getpass(f"Input new password for user '{cf.login}' >> ")
    keyring.set_password("pymail", cf.login, new_password)
    exit()



if start:
    password_from_args = ""
    if "-p" in sys.argv or "--password" in sys.argv:
        if "-p" in sys.argv:
            password_from_args = sys.argv[sys.argv.index("-p") + 1]
        if "--password" in sys.argv:
            password_from_args = sys.argv[sys.argv.index("--password") + 1]

    creds = Credentials( 
            cf.login,
            cf.password if not password_from_args else password_from_args
                        )
    default_interface = cf.default_client.upper()
    config = {
            "smtp":{
                "server": cf.smtp_server,
                "port":cf.smtp_port,
                "timeout": cf.smtp_timeout
            },
            "imap":{
                "server": cf.imap_server,
                "port": cf.imap_port
                }
            }
    if "--test" in sys.argv:
        s = Style(cf.enable_colors)
        fail_msg = s.err + "TESTS FAILED" + s.endc + "\ndetails in pymail.testlog"
        try:
            m = MailClient(creds, config, initialize_smtp=True, initialize_imap=True, silent=is_silent, enable_colors=cf.enable_colors)
            pass_msg = s.green + "TESTS PASSED" + s.endc
            del MailClient
            print(pass_msg)
        except Exception as e:
            with open("pymail.testlog","a") as f:
                f.write(f"{type(e).__name__}: {e}\n\n")
            print(fail_msg)
        finally:
            exit()
    # set interface to open
    if "--cli" in sys.argv or "-i" in sys.argv:
        interface = "CLI"
    elif "--command" in sys.argv:
        interface = "COMMAND"
    else:
        interface = default_interface
    # CLI
    if interface == "CLI":
        m = MailClient(creds, config, enable_colors=cf.enable_colors)
        while start:
            try:
                clear()
                unread = m._get_number_of_mails()["unread"]
                print(f"{m.style.i}Logged as {m.credentials.login}, {m.style.b if unread else ''}Unread: {unread}{m.style.endc}")
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
                    case "9" | "Q" | "EXIT":
                        break
                    case _:
                        print("Not supported input")
                        m.press_enter()
                clear()
            except (KeyboardInterrupt, EOFError):
                break
    # list facorites
    elif "--list-favorites" in sys.argv:
        m = MailClient(creds, config, initialize_smtp=False, initialize_imap=False, silent=is_silent)
        data = m._fetch_all_favorites()
        try:
            from tabulate import tabulate
            print(tabulate(data, headers="keys"))
        except:
            print(json.dumps(data, indent=4))
        exit()
    # headless
    elif interface.startswith("COMMAND"):
        try:
            m = MailClient(creds, config, silent=is_silent, initialize_imap=False)
        except Exception as e:
            if "Username and Password not accepted" in str(e):
                print("Username and password not accepted! Verify that login and password is proper! for more help, use --help!")
                exit()
            raise


        content_type = "plain"
        try:
            # set to
            msg_content = sys.argv[3]
            if sys.argv[1].startswith("-f"):
                recipient = m._fetch_from_favorites(sys.argv[1][2:])
            else:
                recipient = sys.argv[1]
            for i, arg in enumerate(sys.argv):
                if arg == "-c":
                    content_type = sys.argv[i + 1] 
                    continue
                if arg.startswith("-c"):
                    content_type = arg[2:]
                    continue
                if arg == "-o":
                    with open(sys.argv[i + 1],"r") as f:
                        msg_content = f.read()
                    continue
                elif arg.startswith("-o"):
                    with open(arg[2:], "r") as f:
                        msg_content = f.read()
                        continue
            msg = m._setup_message(to=recipient, subject=sys.argv[2], content=msg_content, content_type=content_type)
            m._send_mail(msg)
        except IndexError:
            print("Some arguments are missing! use --help!")
    else:
        print(help_msg)


