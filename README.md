# About this project
This tool was created to help manage a DraftKings league as the commissioner. It used to be a script that was used to generate a blog post template for [Platanofb.com](https://platanofb.com), a GitHub Pages project. Now, this tool is a group of functions that can be called to return data, which makes integration with other projects, like a Flask website, possible. 

One of the new features is `login_to_dk()` which logs in to DraftKings and stores/loads cookies; this enables getting contest details automatically, an improvement over downloading the contest results CSV and supplying the file to the old script. A wiki will be updated to describe usage of each function, although they are appropriately named and comments are included inline with the code.

# Usage
Create a session to be passed to the functions of dkextract
```
import dkextract, requests

s = requests.session()
dkextract.get_all_players(session=s, week=1, year=2020)
```

## Storing DraftKings credentials
This tool will look for DraftKings credentials string in `private_data.py` (relative path). The file should look like this:
```
creds = '{"login":"YOUR@EMAIL.COM","password":"YOUR_PASSWORD","host":"api.draftkings.com","challengeResponse":{"solution":"","type":"Recaptcha"}}'
all_members = ["dk_username1", "dk_username2", "dk_username3"]
values = {
        1: 100,
        2: 50,
        3: 25
    }
```

# Thank you
Thanks for taking a look at my tool. Please feel free to provide feedback or suggestions, but notice, this code was created and written for fun.