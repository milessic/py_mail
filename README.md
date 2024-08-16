# py_mail
Simple Python gmail client


# Usage
pymail can be run either headless or with CLI:

```bash
python3 pymail --interface [or -i] # to run CLI
python3 pymail mail@address.com "Subject text" "Content\nWith New Lines" # to send mail
python3 pymail mail@address.com "Subject text" "<html><body><h1>Content</h1><br>With New Lines</body></body> -c html" # to send mail in HTML format
```

# Configuration
If config file was not found, or is invalid, config file creation will be opened, later it can be manually edited by some text editor.

To find where the config file is stored, use ``--where-is-config``

Config files are stored under ``$HOME/.pymail.conf``


