# py_mail
Simple Python gmail client


# Usage
> [!WARNING]
> Before first run, config file should be created under ``$HOME/.pymail.conf``!

pymail can be run either headless or with CLI:

```bash
python3 pymail --interface [or -i] # to run CLI
python3 pymail mail@address.com "Subject text" "Content\nWith New Lines" # to send mail
python3 pymail mail@address.com "Subject text" "<html><body><h1>Content</h1><br>With New Lines</body></body> -c html" # to send mail in HTML format
```

# Configuration
example config file:
```
my.address@mail.com,Password123
```

Config files are stored under ``$HOME/.pymail.conf``


