# py_mail
Simple Python gmail client


# Usage
> [!WARNING]
> Before first run, config file should be created under ``$HOME/.pymail.conf``!

pymail can be run either headless or with CLI:

```bash
python3 pymail --interface [or -i] # to run CLI
python3 pymail mail@address.com "Subject text" "Content\nWith New Lines" # to send mail
```

# Configuration
example config file:
```
my.address@mail.com,Password123
```

Config files are stored under ``$HOME/.pymail.conf``

# ROADMAP
- [ ] inbox
- [ ] full windows support
- [ ] attachments
- [ ] favorites hadnling for headless instance
  - [x] fetching
  - [x] listing
  - [ ] setting
  - [ ] deleting
- [ ] adding keyword arguments for headless instance
- [ ] add templates
- [ ] script / interface to create config, including adding pymail to PATH
- [ ] add Inbox saving on the storage
