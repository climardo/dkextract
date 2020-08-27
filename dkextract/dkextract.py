import json, re, requests, sys, private_data, pickle, os.path, time
from os import path

# Global value modified by login_to_dk()
login_valid = False

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
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    # URLs used for log in and verifying login attempt
    dk_lobby = "https://draftkings.com/lobby"
    dk_login = "https://api.draftkings.com/users/v3/providers/draftkings/logins?format=json"

    # If cookies_file exists, load cookies_file and try to GET dk_lobby
    if path.exists(cookies_file):
        try:
            load_stored_cookies(session=temp_session, cookies_file=cookies_file)
            if temp_session.get(dk_lobby).status_code == requests.codes.ok:
                # If the attempt was successful, then pass cookies to the original session and return True
                load_stored_cookies(session=session, cookies_file=cookies_file)
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
        if login_attempt.status_code == requests.codes.ok and temp_session.get(dk_lobby).status_code == requests.codes.ok:
            store_cookies(session=temp_session, cookies_file=cookies_file)
            load_stored_cookies(session=session, cookies_file=cookies_file)
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
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    # Static data used in POST request
    weekly_data = '{"sport":"nfl","embed":"stats"}'

    # URL used in post request with parameters (week, year) passed in function
    weekly_url = f"https://live.draftkings.com/api/v2/leaderboards/players/seasons/{year}/weeks/{week}"

    # If login_to_dk is successful, then return JSON payload as a dictionary
    if login_to_dk(session):
        get_weekly = session.post(weekly_url, headers=weekly_headers, data=weekly_data)
        if get_weekly.status_code == requests.codes.ok:
            return json.loads(get_weekly.text)['data']
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
    return get_member_scores(session, contest_id)['leader']['draftGroupId']

def get_member_key(session, contest_id, user_name):
    # Parse through get_member_scores() looking for the member_key of given user_name
    # This value is used by get_member_lineup()
    for member in get_member_scores(session, contest_id)['leaderBoard']:
        if member['userName'] == user_name:
            member_key = member['entryKey']
            break
        else:
            member_key = 0
    return member_key

def get_member_lineup(session, contest_id, user_name):
    # Use get_draft_id() and get_member_key() to get values needed for roster_url
    draft_id = get_draftid(session, contest_id)
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
    member_scores = get_member_scores(session, contest_id)['leaderBoard']
    for member in member_scores:
        user_name = member['userName']
        all_lineups.append(get_member_lineup(session, contest_id, user_name)['entries'][0])
    return all_lineups

def get_all_drafted(session, contest_id):
    # Return a list of all drafted players without duplcates
    # players_name[] is used to compare each players with those already added to all_players[]
    all_players = []

    # Filter through each member's list of players contained within get_member_lineup() output
    for member in get_member_scores(session, contest_id)['leaderBoard']:
        user_name = member['userName']
        user_lineup = get_member_lineup(session, contest_id, user_name)['entries'][0]['roster']['scorecards']
        for player in user_lineup:
            # Add unique players to all_players list 
            if not any(d['displayName'] == player['displayName'] for d in all_players):
                all_players.append(player)
    return all_players

def set_fpts_salary(all_players):
    # Provide a list of all players, probably using get_all_players()
    # This function will return the list after adding ['fantasyPointsPerSalary'] to each item

    # First, filter the list for only players with stats and salary
    players = [player for player in all_players if player.get('salary') and player['stats']]

    for player in players:
        fpts_salary = player['fantasyPoints'] / player['salary']
        player['fantasyPointsPerSalary'] = fpts_salary

    return players

def set_display_name(all_players):
    # Provide a list of all players, probably using get_all_players()
    # This function will return the list after adding ['displayName'] to each item
    for player in all_players:
        full_name = player['firstName']
        if player['lastName']:
            full_name += f" {player['lastName']}"
            
        player['displayName'] = full_name

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

def get_drafted_by(player, all_lineups):
    # Return a list of members who drafted the player provided in the command arguments
    # all_lineups should include players with set_display_name() applied
    player_name = player['displayName']
    members = []
    for member in all_lineups:
        if re.search(f'"displayName": "{player_name}"', json.dumps(member), re.M):
            members.append(member['userName'])
    
    return members

def get_draft_dodger(all_players, all_drafted):
    # This function assumes you use get_all_players() to supply all_players and get_all_drafted() for all_drafted
    # Create a list of players from all_players that are not in all_drafted
    # all_players may not containt displayName so try to compare first and if it fails then set_display_name() first
    undrafted_players = []
    try:
        temp = all_players[0]['displayName']
    except:
        all_players = set_display_name(all_players)
    
    for player in all_players:
        if not any(d['displayName'] == player['displayName'] for d in all_drafted):
            undrafted_players.append(player)

    draft_dodger = max(undrafted_players, key=lambda x: x['fantasyPoints'])

    return draft_dodger

def generate_results(session, contest_id, week, year=2020):
    # Returns a dict including the week and list of members with their rank and fantasyPoints
    # Start with an empty list
    members_filtered = []
    # Get a list of all members to be filtered
    weekly = get_member_scores(session, contest_id)['leaderBoard']
    for member in weekly:
        # Extract specific keys for each member and add as dict to members_filter[]
        member_weekly = {"userName": member['userName'], "rank": member['rank'], "fantasyPoints": member['fantasyPoints']}
        members_filtered.append(member_weekly)
    
    # Generate superlatives
    all_players = set_display_name(get_all_players(session, week, year))
    all_drafted = get_all_drafted(session, contest_id)
    all_lineups = get_all_lineups(session, contest_id)

    mvp = get_mvp(all_players)
    mvp['draftedBy'] = get_drafted_by(mvp, all_lineups)
    sleeper = get_sleeper(all_players)
    sleeper['draftedBy'] = get_drafted_by(sleeper, all_lineups)
    bust = get_bust(all_players)
    bust['draftedBy'] = get_drafted_by(bust, all_lineups)
    draft_dodger = get_draft_dodger(all_players, all_drafted)
    
    # Add the week as a seprate value and add members_filtered[] as a value of "members"
    members_dict = {"week": int(week), "contest_id": contest_id, "members": members_filtered, "mvp": mvp, "sleeper": sleeper, "bust": bust, "draft_dodger": draft_dodger}

    return members_dict

def add_weekly_json(json_file, session, contest_id, week, year=2020):
    # If the json_file does not exist or contains invalid data, start wih an empty list
    try:
        with open(json_file) as f:
            original = json.loads(f.read())
    except:
        original = []

    # Get results of the provided week and add it to the existing list
    current_week = generate_results(session, contest_id, week, year)
    original.append(current_week)
    
    # Return the list in JSON format
    return json.dumps(original)