import json, re, requests, sys, private_data, pickle, os.path, time
from os import path
# Used to test processing time
start_time = time.time()

# Test values
week = "16"
year = "2019"
contestid = "83207559"

# Global value modified b login_to_dk()
login_valid = False

# List of DraftKings URLS for GET and POST requests
dk_live= f"https://live.draftkings.com/sports/nfl/seasons/{year}/week/{week}/games/all"

# Create a session to maintain cookies
s = requests.session()

def login_to_dk(session, cookies_file='stored_cookies', login_data=private_data.creds, strict=False):
    # The following lines read a global variable to reduce the time it takes to process this function
    # Without this check, calling this function would always verify cookies each time it is called
    # This function will run at least once, but can be presumed True afterwards
    # Set the strict parameter to True when running his function to force cookie verification
    global login_valid
    if login_valid and not strict:
        return True
    # Session used to check cookies before they are passed to 'session' object
    temp_session = requests.session()
    
    # Headers used when logging in to DraftKings
    login_headers = {
        'Host': 'api.draftkings.com',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '"\\Not;A\"Brand";v="99", "Google Chrome";v="85", "Chromium";v="85"',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 13310.41.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.59 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://www.draftkings.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.draftkings.com/account/sitelogin/false?returnurl=%2Flobby',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # URLs used for log in and verifying login attempt
    dk_lobby = "https://draftkings.com/lobby"
    dk_login = "https://api.draftkings.com/users/v3/providers/draftkings/logins?format=json"

    # If cookies_file exists, load cookies_file and try to GET dk_lobby
    if path.exists(cookies_file):
        try:
            load_stored_cookies(session=temp_session, cookies_file='stored_cookies')
            if temp_session.get(dk_lobby).status_code == requests.codes.ok:
                # If the attempt was successful, then pass cookies to the original session and return True
                load_stored_cookies(session=session, cookies_file='stored_cookies')
                login_valid = True
                return True
        except:
            # There is a problem with the data in the provided cookies_file
            # Remove cookies_file and run this function again to reach the following else statement
            os.remove(cookies_file)
            return login_to_dk(session)
    else:
        # Get new cookies to be stored in cookies_file
        login_attempt = temp_session.post(dk_login, headers=login_headers, data=login_data)
        # If login and GET dk_lobby are successful, then store the cookies cookies_file, pass cookies to the original session and return True
        if login_attempt.status_code == requests.codes.ok and session.get(dk_lobby).status_code == requests.codes.ok:
            store_cookies(session=temp_session, cookies_file='stored_cookies')
            load_stored_cookies(session=session, cookies_file='stored_cookies')
            login_valid = True
            return True
        # If login and GET fail, then output the status code, headers and text of the login attempt
        else:
            print(f"Failed login attempt, status code: {login_attempt.status_code}.\nHeaders:\n{login_attempt.headers}\nText:{login_attempt.text}")
            login_valid = False
            return False  

def load_stored_cookies(session, cookies_file='stored_cookies'):
    # Load stored cookies to session
    with open(cookies_file, 'rb') as f:
        session.cookies.update(pickle.load(f))

def store_cookies(session, cookies_file='stored_cookies'):
    # Store new session cookies to file
        with open(cookies_file, 'wb') as f:
            pickle.dump(session.cookies, f)

def get_all_players(session, week, year=2020):
    # Function to obtain JSON (as a dictionary) of all player stats including fantasy points and salary
    # Header used in POST request
    weekly_headers = {
        'Host': 'live.draftkings.com',
        'Connection': 'keep-alive',
        'Content-Length': '31',
        'Origin': 'https://live.draftkings.com',
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 12499.46.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.81 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': f"https://live.draftkings.com/sports/nfl/seasons/{year}/week/{week}/games/all",
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,la;q=0.8'
    }

    # Static data used in POST request
    weekly_data = '{"sport":"nfl","embed":"stats"}'

    # URL used in post request with parameters (week, year) passed in function
    weekly_url = f"https://live.draftkings.com/api/v2/leaderboards/players/seasons/{year}/weeks/{week}"

    # If login_to_dk is successful, then return JSON payload as a dictionary
    if login_to_dk(session):
        get_weekly = session.post(weekly_url, headers=weekly_headers, data=weekly_data)
        if get_weekly.status_code == requests.codes.ok:
            return json.loads(get_weekly.text)["data"]
        else:
            return {}
    else:
        return {}

def get_member_scores(session, contest_id):
    # Set leaderboard address using contest_id supplied to function
    leaderboad_url = f"https://api.draftkings.com/scores/v1/leaderboards/{contest_id}?format=json&embed=leaderboard"

    # If login_to_dk is successful, then return JSON payload as a dictionary
    if login_to_dk(session):
        get_leaderboard = session.get(leaderboad_url)
        if get_leaderboard.status_code == requests.codes.ok:
            return json.loads(get_leaderboard.text)
        else:
            return {}
    else:
        return {}

def get_draftid(session, contest_id):
    # Value used for obtaining individual member lineups
    return get_member_scores(session, contest_id)["leader"]["draftGroupId"]

def get_member_key(session, contest_id, user_name):
    # Parse through get_member_scores() looking for the member_key of given user_name
    # This value is used by get_member_lineup()
    for member in get_member_scores(session, contest_id)["leaderBoard"]:
        if member["userName"] == user_name:
            member_key = member["entryKey"]
            break
        else:
            member_key = 0
    return member_key

def get_member_lineup(session, contest_id, user_name):
    # Use get_draft_id() and get_member_key() to get values needed for roster_url
    draft_id = get_draftid(session, contestid)
    member_key = get_member_key(session, contest_id, user_name)

    # The API endpoint for a specific user's lineup
    roster_url = f"https://api.draftkings.com/scores/v2/entries/{draft_id}/{member_key}?format=json&embed=roster"
    # If login_to_dk is successful, then return JSON payload as a dictionary
    if login_to_dk(session):
        get_roster = session.get(roster_url)
        if get_roster.status_code == requests.codes.ok:
            return json.loads(get_roster.text)
        else:
            return {}
    else:
        return {}

def get_all_lineups(session, contest_id):
    # Get a list of each member's lineup
    all_lineups = []
    for member in get_member_scores(session, contest_id)["leaderBoard"]:
        user_name = member["userName"]
        all_lineups.append(get_member_lineup(session, contest_id, user_name))
    return all_lineups

def list_all_drafted(session, contest_id):
    # Return a list of all drafted players without duplcates
    # players_name[] is used to compare each players with those already added to all_players[]
    all_players = []

    # Filter through each member's list of players contained within get_member_lineup() output
    for member in get_member_scores(session, contest_id)["leaderBoard"]:
        user_name = member["userName"]
        user_lineup = get_member_lineup(session, contest_id, user_name)["entries"][0]["roster"]["scorecards"]
        for player in user_lineup:
            # Add unique players to all_players list 
            if not any(d['displayName'] == player['displayName'] for d in all_players):
                all_players.append(player)
    return all_players

def set_fpts_salary(all_players):
    # Provide a list of all players, probably using get_all_players()
    # This function will return the list after adding ["fantasyPointsPerSalary"] to each item

    # First, filter the list for only players with stats and salary
    players = [player for player in all_players if player.get('salary') and player['stats']]

    for player in players:
        fpts_salary = player['fantasyPoints'] / player['salary']
        player['fantasyPointsPerSalary'] = fpts_salary

    return players

def set_display_name(all_players):
    # Provide a list of all players, probably using get_all_players()
    # This function will return the list after adding ["displayName"] to each item
    for player in all_players:
        full_name = player['firstName']
        if player['lastName']:
            full_name += f" {player['lastName']}"
            
        player["displayName"] = full_name

    return all_players

def get_bust(all_players):
    # Create a list (bust_players) of dicts where salary is greater than or equal to 5000
    try:
        bust_players = [x for x in all_players if x.get('salary') >= 5000]
    except:
        all_players = set_fpts_salary(all_players)
        bust_players = [x for x in all_players if x.get('salary') >= 5000]

    # From the previously create list, Assign the item with the lowest fantasyPointsPerSalary to bust
    bust = min(bust_players, key=lambda x: x['fantasyPointsPerSalary'])

    return bust

def get_mvp(all_players):
    # Return the item/player with highest fantasyPoints
    mvp = max(all_players, key=lambda x: x['fantasyPoints'])

    return mvp

def get_sleeper(all_players):
    # Return the item/player with highest fantasyPointsPerSalary
    # If there is an error, it is likely because the key doesn't exist. Use set_fpts_salary() to correct this problem and try again
    try:
        sleeper = max(all_players, key=lambda x: x['fantasyPointsPerSalary'])
    except:
        all_players = set_fpts_salary(all_players)
        sleeper = max(all_players, key=lambda x: x['fantasyPointsPerSalary'])

    return sleeper

def get_draft_dodger(all_players, all_drafted):
    # This function assumes you use get_all_players() to supply all_players and list_all_drafted() for all_drafted
    # Create a list of players from all_players that are not in all_drafted
    # all_players may not containt displayName so try to compare first and if it fails then set_display_name() first
    undrafted_players = []
    try:
        temp = all_players[0]['displayName']
    except:
        all_players = set_display_name(all_players)
    finally:
        for player in all_players:
            if any(d['displayName'] == player['displayName'] for d in all_drafted):
                undrafted_players.append(player)

    draft_dodger = max(undrafted_players, key=lambda x: x['fantasyPoints'])

    return draft_dodger

# Example commands used to verify code
#all_players = get_all_players(s, 16, 2019)
all_drafted = list_all_drafted(s, contestid)
print(len(all_drafted))
print("--- %s seconds ---" % (time.time() - start_time))
exit()