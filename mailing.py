import re
import json
import re
import readline
from tabulate import tabulate
import poplib
import imaplib
from email import message_from_bytes
from email.header import decode_header, make_header
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def clear():
    os.system("cls" if os.name=="nt" else "clear")

class Style:
    # classes
    b = "\33[1m"
    i = "\33[3m"
    err = "\33[38;1;41m"
    warn = "\33[38;1;93m"
    # colors
    deep_green = "\33[38;1;96m"
    green = "\33[92m"
    endc = "\33[0m"

class Credentials:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __str__(self):
        return f"{self.login}, ******"
    def __repr__(self):
        return f"{self.login}, ******"

class MailClient:
    def __init__(self, credentials, config, silent:bool=False, initialize_smtp:bool=True, initialize_pop3:bool=True):
        self.messages = {}
        self.message_counts = {}
        self.debug = False
        self.silent = silent
        self.initialize_smtp = initialize_smtp 
        self.initialize_pop3 = False   #initialize_pop3
        self.initialize_imap = initialize_pop3
        self.initialize_credentials = self.initialize_smtp or self.initialize_pop3
        if self.initialize_credentials:
            if not silent:
                clear()
                print("Loading py_mail....")
            self.credentials = credentials
            self.config = config
        if initialize_smtp:
            # setup smtp
            try:
                # print("Starting server...")
                self.s = smtplib.SMTP(self.config["smtp"]["server"],
                                       self.config["smtp"]["port"],
                                      timeout=self.config["smtp"]["timeout"]
                                      )
                self.s.starttls()
                self.s.ehlo()
                self.s.login(self.credentials.login, self.credentials.password) # print("Server started!")
            except Exception as e:
                print(f"""server: '{self.config["smtp"]["server"]}'.""")
                raise AssertionError(f"{Style.err}Error when connecting to SMTP server! {type(e).__name__}: {e}{Style.endc}")
        # setup IMAP
        if self.initialize_imap:
            try:
                self.i = imaplib.IMAP4_SSL("imap.gmail.com")
                self.i.login(user=self.credentials.login, password=self.credentials.password)
            except Exception as e:
                print(f"{Style.err}Error connecting to IMAP server! {type(e).__name__}: {e}{Style.endc}")
                input("Press ENTER to continue")
        # setup pop3
        if initialize_pop3:
            try:
                self.p = poplib.POP3_SSL(self.config["pop3"]["host"], self.config["pop3"]["port"])
                self.p.user(self.credentials.login)
                self.p.pass_(self.credentials.password)
            except Exception as e:
                print(f"""server: '{self.config["pop3"]["server"]}'.""")
                raise AssertionError(f"{Style.err}Error when connecting to POP3 server! {type(e).__name__}: {e}{Style.endc}")

        # Open Favorites
        self.favorites_file = f"{os.getenv('HOME')}/.pymail_favorites.json"
        try:
            with open(self.favorites_file, "r") as f:
                self.favorites = json.load(f)
        except FileNotFoundError:
            with open(self.favorites_file,"w") as f:
                f.write("{}")
                self.favorites = {}
        except Exception as e:
            if not silent:
                print("{Style.err}Could not load 'favorites.json'!{Style.endc}")
                print(e)

    def __del__(self):
        if not self.initialize_smtp:
            return
        try:
            self.s.quit()
            if not self.silent:
                print("Server connection closed...")
        except AttributeError:
            pass
        except Exception:
            pass

    def show_favorites(self):
        print(f"{Style.deep_green}=== FAVORITES{Style.endc}")
        if not len(self.favorites):
            print("\t-no favorites added")
        for k,v in self.favorites.items():
            print(f"\t-{k}\t-{v}")
        self.press_enter()
    
    def add_to_favorites(self):
        print("f{Style.deep_green}=== ADD FAVORITES{styles.endc}")
        mail = input(f"MAIL ADDRESS >>>{Style.endc} ")
        alias = input(f"ALIAS >>>{Style.endc} ")
        confirm = True if input(f"Mail: '{mail}', alias: '{alias}'\nDo you confirm? y/n ").lower().startswith("y") else False
        if confirm:
            print(f"{Style.deep_green}{alias} added to Favorites.{Style.endc}")
            self.favorites[alias] = mail
        self.save_favorites()
        self.press_enter()

    def remove_from_favorites(self):
        print("{Style.deep_green}=== REMOVE FAVORITES{Style.endc}")
        alias = input("ALIAS TO REMOVE >>>{Style.endc} ")
        if alias not in self.favorites:
            print(f"{Style.deep_green}There are no '{alias}' in FAVORITES!{Style.endc}")
            self.press_enter()
            return
        confirm = True if input(f"Mail: '{self.favorites[alias]}', alias: '{alias}'\nDo you confirm deletion? y/n ").lower().startswith("y") else False
        if confirm:
            print(f"{Style.warn}{alias} deleted from Favorites.{Style.endc}")
            del self.favorites[alias]
        self.save_favorites()
        self.press_enter()

    def save_favorites(self):
        try:
            with open(self.favorites_file, "w") as f:
                f.write(json.dumps(self.favorites, indent=4))
        except Exception as e:
            print(e)
            self.press_enter()

    def _fetch_from_favorites(self, name:str) -> str:
        try:
            return self.favorites[name]
        except KeyError:
            raise KeyError(f"Could not find '{name}' in favorites!")

    def _fetch_all_favorites(self) -> list:
        data = []
        for a,m in self.favorites.items():
            data.append({"alias":a, "mail":m})
        return data


    def _setup_message(self, to, subject, content) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["To"] = to
        content = content.split(sep="\\n")
        content = "\n".join(content)
        msg.attach(MIMEText(content, "plain"))
        return msg

    def _send_mail(self, msg):
        self.s.sendmail(self.credentials.login, msg["To"], msg.as_string())

    def send_mail(self):
        try:
            print(f"{Style.deep_green}=== SEND NEW MAIL{Style.endc}")
            self.deb("Creating message..")
            msg = MIMEMultipart()
            msg["Subject"] = input(f"{Style.deep_green}SUBJECT >>>{Style.endc} ")
            recipients_raw = input(f"{Style.deep_green}RECIPIENTS >>>{Style.endc} ").split(",")
            recipients = ",".join([self.favorites[r] if r in self.favorites else r for r in recipients_raw])
            self.deb("set recipients")

            msg["To"] = recipients
            msg.attach(MIMEText(self.collect_multiline(f"{Style.green}TYPE BODY:"), "plain"))
            self.deb("Sending mail...")
            self._send_mail(msg)
            self.deb("Sent mail...")
            print(f"{Style.deep_green}Mail sent!{Style.endc}")
            print(f"recipients: {recipients}")
            self.press_enter()
        except Exception as e:
            print(f"{Style.err}Could not send mail due to:{Style.endc}\n{Style.warn}{type(e).__name__}: {e}{Style.endc}")
            self.press_enter()
            return
    
    def collect_multiline(self, msg):
        print(msg)
        x = input(f">>>{Style.endc} ")
        inputs = []
        reset_c = 0
        while reset_c < 2:
            inputs.append(x)
            x = input(f"{Style.green}>>>{Style.endc} ")
            if x == "":
                reset_c += 1
            else:
                reset_c = 0
        return "\n".join(inputs)
    
    def get_number_of_mails(self, r=0):
        #message_count, total_size = self.p.stat()
        try:
            num_messages = len(self.p.list()[1])
            return num_messages
        except:
            if r > 10:
                raise
            r+=1
            return self.get_number_of_mails(r=r)

        return str(message_count)
    #self.press_enter()

    def press_enter(self):
        input("Press ENTER to continue...")

    def show_inbox(self):
        clear()
        print("=== INBOX")
        self._fetch_emails_imap()
        print(tabulate(self.messages, headers="keys"))
        inbox_input = input("[0] Read {Num} - [1] Reply {Num} - [2] Reload - [9] Exit\n>>> ")
        match inbox_input.upper():
            case "0" | "READ":
                self.not_implemented()
                self.show_inbox()
            case "1" | "REPLY":
                self.not_implemented()
                self.show_inbox()
            case "2" | "RELOAD":
                self._fetch_emails_imap(hard=True)
                self.show_inbox()
            case "9" | "EXIT":
                return
    
    def _get_number_of_mails(self) -> dict:
        if self.message_counts == {}:
            self._fetch_emails_imap()
        return self.message_counts

    def _fetch_emails_imap(self, hard:bool=False):
        if len(self.messages) != 0:
            if not hard:
                return
        print("Looking for new mails...")
        status, messages = self.i.select('INBOX')    
        if status != "OK": exit("Incorrect mail box")
        
        msg_count = {"all":0, "unread":0}
        msgs = []
        msg_i = 0
        for i in range(1, int(messages[0]) + 1):
            #res, msg = self.i.fetch(str(i), '(RFC822 FLAGS)')  RFC822 makrs msgs Seen
            res, msg = self.i.fetch(str(i), '(BODY.PEEK[] FLAGS)')
            if res != "OK":
                continue
            for response in msg:
                if isinstance(response, tuple):
                    msg = message_from_bytes(response[1])
                    res, flag_data = self.i.fetch(str(i), '(FLAGS)')
                    msg_flags = flag_data[0].decode()
                    msg_seen = '\\Seen' in msg_flags
                    if not msg_seen:
                        msg_count["unread"] +=1
                    msg_count["all"] += 1
                    msg_subject = f"{Style.endc if msg_seen else Style.b}" + msg["Subject"] + Style.endc
                    msg_from = msg["From"]
                    decoded_msg_from = str(make_header(decode_header(msg_from)))
                    decoded_msg_from = re.sub(r"(<)([\s\S])*", "", decoded_msg_from)
                    msgs.append({"Num": msg_i,"Subject": msg_subject, "From": decoded_msg_from})
                    msg_i += 1
        self.messages = msgs
        self.message_counts = msg_count

    def deb(self, msg):
        if self.debug:
            print(msg)

    def not_implemented(self, msg:str=""):
        input(Style.warn + "Not implemented! press ENTER to continue" + msg + Style.endc)



