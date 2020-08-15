# About this project
This tool was created to help manage a DraftKings league as the commissioner. A "functional" version was originally created in `weekly.py` which simply takes user input on the command line and returns text. As of 2020-08-15, an updated version is under development in `test.py` with proper functions that can be called to return data with the intent of integrating it into a Flask website. One of the new features is `login_to_dk()` whichwhich logs in to DraftKings and store the cookies to a file; this enables getting contest details automatically. More usage information will be added here in the future.

# Storing DraftKings credentials
By default, this tool will look for DraftKings credentials in `./private_data.py`. The file should look like this:

    creds = '{"login":"YOUR@EMAIL.COM","password":"YOUR_PASSWORD","host":"api.draftkings.com","challengeResponse":{"solution":"","type":"Recaptcha"}}'

# To-do list
- Determine the best way to store and retrieve results, likely a YAML file that is compatible with GitHub Pages
- `update_season_results()`: Add member results to a list, including weekly fantasyPoints, rank and winnings

# Thank you
Thanks for taking a look at my tool. Please feel free to provide feedback or suggestions. Note, this code was created and written for fun.