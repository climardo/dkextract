# About this project
This tool was created to help manage a DraftKings league as the commissioner. It used to be a script that was used to generate a blog post template for [Platanofb.com](https://platanofv.com), a GitHub Pages project. Now, this tool is a group of functions that can be called to return data, which makes integration wit other projects, like a Flask website, possible. 

One of the new features is `login_to_dk()` which logs in to DraftKings and store the cookies to a file; this enables getting contest details automatically, an improvement over downloading the contest results CSV and supplying the file to the old script. A wiki will be updated to describe usage of each function, although they are appropriately named and coments are included inline with the code.

# Storing DraftKings credentials
By default, this tool will look for DraftKings credentials in `./private_data.py`. The file should look like this:
```
creds = '{"login":"YOUR@EMAIL.COM","password":"YOUR_PASSWORD","host":"api.draftkings.com","challengeResponse":{"solution":"","type":"Recaptcha"}}'
```

# To-do list
- `get_latest_contest_id()`: Get the contestId of the latest contest for the logged in user
- `get_week()` & `get_year()`: figure out if the date and year can be extracted from DraftKings responses to existing POST and GET requests. Possibly something related to the `contest_id`.
- Create a wiki

# Thank you
Thanks for taking a look at my tool. Please feel free to provide feedback or suggestions, but notice, this code was created and written for fun.