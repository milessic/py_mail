import configparser
from pathlib import Path
from getpass import getpass
import os
import keyring


class Config:
    def __init__(self):
        self.config_path = f"{os.getenv('HOME')}/.pymail.conf"
        self.c = configparser.ConfigParser()
        try:
            self.c.read(self.config_path)
            self.login
            self.default_client
            self.enable_colors
            self.smtp_port
            self.smtp_server
            self.smtp_timeout
            self.imap_port
            self.imap_server
        except Exception as e:
            print("Config does not exist, or could not be loaded")
            self.setup_new_config()

    def setup_new_config(self):
        print("=== PY_MAIL CONFIGURATION")
        while True:
            try:
                #config_path = input("provide config path or leave empty for HOME [HOME] >> ") # TODO in some future
                config_path = "HOME"
                if not config_path or config_path.upper() == "HOME":
                    home_path = os.getenv("HOME")
                    self.config_path = Path(home_path, ".pymail.conf")
                    break
                self.config_path = Path(config_path)
                self.c.read(self.config_path)
                break
            except:
                print(f"Invalid path provided! {config_path} Please try again or use default option")
        # set credentials
        print("---User Account")
        self._set_str_config("login e-mail address", "CREDENTIALS", "login")
        password = getpass("password: >> ")
        keyring.set_password(f"pymail", self.login, password)

        # setup preferences
        print("\n---Preferences")
        self._set_str_config("preffered client CLI/COMMAND LINE", "PREFERENCES", "default_client", "CLI")
        self._set_bool_config("Enable Colors (ASCII) ", default=True, section="PREFERENCES", config_name="enable_colors")

        # setup server configuraionts
        # SMTP
        print("\n---SMTP")
        self._set_str_config("provide SMTP server", "SMTP", "smtp_server", "smtp.gmail.com")
        self._set_str_config("provide SMTP port", "SMTP", "smtp_port", "587")
        self._set_str_config("provide SMTP timeout", "SMTP", "smtp_timeout", "120")
        # IMAP
        print("\n---IMAP")
        self._set_str_config("provide IMAP server", "IMAP", "imap_server", "imap.gmail.com")
        self._set_str_config("provide IMAP port", "IMAP", "imap_port", "995")

        
        # finish
        print(f"Configuration properly created under {self.config_path}\n\n")
        continue_app = input("Open application? [Y]/N >> ").upper()
        if continue_app == "Y" or not continue_app:
            return
        print("Closing...")
        exit()

    def _save_config(self):
        with open(self.config_path, "w") as f:
            self.c.write(f)

    def _set_str_config(self, msg:str,  section:str, config_name:str, default:str|None=None):
        value = ""
        while True:
            try:
                msg += (f" [{default}]" if default is not None else "") + " >> " 
                value = input(msg)
                if not value:
                    if default is None:
                        continue
                    value = default
                break
            except:
                pass
        try:
            self.c.set(section, config_name, value)
        except configparser.NoSectionError:
            self.c.add_section(section)
            self.c.set(section, config_name, value)
        self._save_config()



    def _set_bool_config(self, msg:str, default:bool, section:str, config_name:str):
        supported_values = ["Y", "N", "YES", "NO"]
        value = ""
        while True:
            try:
                msg += (" [Y]/N " if default else " Y/[N] ") + ">> "
                value = input(msg).upper()
                if value in supported_values or value == "":
                    if value == "":
                        value = "Y" if default else "N"
                    break
            except:
                pass
            print(f"Not valid input - '{value}'! valids one are 'Y' or 'N'!")
        value_as_int = str(int(value.startswith("Y")))
        self.c.set(section, config_name, value_as_int)
        self._save_config()

    @property
    def login(self):
        return self.c["CREDENTIALS"]['login']

    @property
    def password(self):
        return keyring.get_password(f"pymail", self.login)

    @property
    def default_client(self):
        return self.c["PREFERENCES"]['default_client']

    @property
    def enable_colors(self):
        return bool(int(self.c["PREFERENCES"]["enable_colors"]))

    @property
    def smtp_server(self):
        return self.c["SMTP"]["smtp_server"]
    
    @property
    def smtp_port(self):
        return int(self.c["SMTP"]["smtp_port"])

    @property
    def smtp_timeout(self):
        return int(self.c["SMTP"]["smtp_timeout"])

    @property
    def imap_server(self):
        return self.c["IMAP"]["imap_server"]

    @property
    def imap_port(self):
        return int(self.c["IMAP"]["imap_port"])

