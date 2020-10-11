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

## DraftKings credentials and other values
This tool will look for DraftKings credentials in the following environment variables:
```
export DKUSER=dkuser@email.com
export DKPASS=dkp@ssw0rd
```

Some other values that are not obvious when using the tool:
```
all_members = set(["dk_username1", "dk_username2", "dk_username3"])
winning_values = {1: 100, 2: 50, 3: 25}
```
- `all_members` is a **set** of all DraftKings member names
- `winning_values` is a value assigned to a rank. In this example, first place (rank 1 or `1:`) is assigned a value of `100`. Pass this to `generate_results()`

# Thank you
Thanks for taking a look at my tool. Please feel free to provide feedback or suggestions, but notice, this code was created and written for fun.