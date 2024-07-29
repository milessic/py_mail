import json
import poplib
from email import parser
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class MailClient:
    def __init__(self, credentials, config, silent:bool=False):
        if not silent:
            print("Loading py_mail....")
        self.credentials = credentials
        self.config = config
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
                print("\33[38;1;91mCould not load 'favorites.json'!\33[0m")
                print(e)
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
            raise AssertionError(f"\33[41mError when connecting to SMTP server! {type(e).__name__}: {e}\33[0m")
        # setup pop3
        try:
            self.p = poplib.POP3_SSL(self.config["pop3"]["host"], self.config["pop3"]["port"])
            self.p.user(self.credentials.login)
            self.p.pass_(self.credentials.password)
        except Exception as e:
            print(f"""server: '{self.config["pop3"]["server"]}'.""")
            raise AssertionError(f"\33[41mError when connecting to POP3 server! {type(e).__name__}: {e}\33[0m")

    def __del__(self):
        try:
            self.s.quit()
            print("Server connection closed...")
        except AttributeError:
            pass
        except Exception as e:
            pass

    def show_favorites(self):
        print("\33[38;1;96m=== FAVORITES\33[0m")
        if not len(self.favorites):
            print("\t-no favorites added")
        for k,v in self.favorites.items():
            print(f"\t-{k}\t-{v}")
        self.press_enter()
    
    def add_to_favorites(self):
        print("\33[38;1;96m=== ADD FAVORITES\33[0m")
        mail = input("MAIL ADDRESS >>>\33[0m ")
        alias = input("ALIAS >>>\33[0m ")
        confirm = True if input(f"Mail: '{mail}', alias: '{alias}'\nDo you confirm? y/n ").lower().startswith("y") else False
        if confirm:
            print(f"\33[38;92m{alias} added to Favorites.\33[0m")
            self.favorites[alias] = mail
        self.save_favorites()
        self.press_enter()

    def remove_from_favorites(self):
        print("\33[38;1;96m=== REMOVE FAVORITES\33[0m")
        alias = input("ALIAS TO REMOVE >>>\33[0m ")
        if alias not in self.favorites:
            print(f"\33[38;93mThere are no '{alias}' in FAVORITES!\33[0m")
            self.press_enter()
            return
        confirm = True if input(f"Mail: '{self.favorites[alias]}', alias: '{alias}'\nDo you confirm deletion? y/n ").lower().startswith("y") else False
        if confirm:
            print(f"\33[38;93m{alias} deleted from Favorites.\33[0m")
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
            print("\33[38;1;96m=== SEND NEW MAIL\33[0m")
            msg = MIMEMultipart()
            msg["Subject"] = input("\33[38;92mSUBJECT >>>\33[0m ")
            recipients_raw = input("\33[38;92mRECIPIENTS >>>\33[0m ").split(",")
            recipients = ",".join([self.favorites[r] if r in self.favorites else r for r in recipients_raw])

            msg["To"] = recipients
            msg.attach(MIMEText(self.collect_multiline("\33[92mTYPE BODY:"), "plain"))
            self._send_mail(msg.as_string())
            print("\33[38;1;92mMail sent!\33[0m")
            print(f"recipients: {recipients}")
            self.press_enter()
        except Exception as e:
            print(f"\33[38;1;91mCould not send mail due to:\33[0m\n\33[38;93m{type(e).__name__}: {e}")
            self.press_enter()
            return
    
    def collect_multiline(self, msg):
        print(msg)
        x = input(">>>\33[0m ")
        inputs = []
        reset_c = 0
        while reset_c < 2:
            inputs.append(x)
            x = input("\33[92m>>>\33[0m ")
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
        print("=== INBOX")
        all_messages = [self.p.retr(i+1)[1] for i in range(self.get_number_of_mails())]
        print(all_messages[2][0])
        print(all_messages[2][1])
        print(all_messages[2][3])
        input()
        max_on_page = 30 
        messages = max_on_page if max_on_page > self.get_number_of_mails() else self.get_number_of_mails()
        msgs = [self.p.retr(0)]
        for m in msgs:
            print(f"- {m['from']}\t\t {m['subject']}")



"""
# Gmail POP3 server details
HOST = 'pop.gmail.com'
PORT = 995

# User credentials
USER = 'your-email@gmail.com'
PASSWORD = 'your-email-password'  # Use an app-specific password if you have 2FA enabled

def fetch_emails():
    # Connect to the server
    pop_conn = poplib.POP3_SSL(HOST, PORT)

    # Authenticate
    pop_conn.user(USER)
    pop_conn.pass_(PASSWORD)

    # Get message count
    message_count, total_size = pop_conn.stat()
    print(f'Total messages: {message_count}')

    # Fetch all messages from the server
    messages = [pop_conn.retr(i) for i in range(1, message_count + 1)]

    # Combine message parts and parse them
    messages = ["\n".join([line.decode('utf-8') for line in msg[1]]) for msg in messages]
    messages = [parser.Parser().parsestr(msg) for msg in messages]

    # Print subject and sender of each message
    for message in messages:
        print(f"Subject: {message['subject']}")
        print(f"From: {message['from']}\n")

    # Disconnect from the server
    pop_conn.quit()

"""


