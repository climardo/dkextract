#! /usr/bin/python3

import json, re, requests
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

# Capture user input to assign values to variables
week = str(input('2019 NFL week #: '))
contest_id = str(input('Contest ID: '))
results_file = input('Path to contest standings files: ')

# Get list of bye_teams by downloading and parsing data from Yahoo Sports
get_game_data = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues=nfl&week={}&season=current'.format(str(int(week) + 1))
r = requests.get(url=get_game_data)
game_data = r.json()['service']['scoreboard']
bye_teams_raw = set(game_data['bye_teams'])
bye_teams = []
for team in game_data['teams']:
    if team in bye_teams_raw:
        bye_teams.append(game_data['teams'][team]['display_name'])
bye_teams = ', '.join(bye_teams)

# Get data from live.draftkings.com for week specified by user input
data = '{"sport":"nfl","embed":"stats"}'

# Visit dk_live to obtain cookies used to make POST request to dk_api
dk_live = 'https://live.draftkings.com/sports/nfl/seasons/2019/week/{}/games/all'.format(week)
dk_api = 'https://live.draftkings.com/api/v2/leaderboards/players/seasons/2019/weeks/{}'.format(week)

# Create a session to maintain cookies
s = requests.session()
s0 = s.get(dk_live)
# Create headers for POST request
headers = {
    'Host': 'live.draftkings.com',
    'Connection': 'keep-alive',
    'Content-Length': '31',
    'Origin': 'https://live.draftkings.com',
    'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 12499.46.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.81 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://live.draftkings.com/sports/nfl/seasons/2019/week/{}/games/all'.format(week),
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8'
}
# Make a post request including headers and data
dk_resp = s.post(dk_api, headers=headers, data=data)

# Convert dk_resp (string) into a JSON object (dict)
raw = json.loads(dk_resp.text).get('data')
# Include only players with stats and salary, assuming players with neither were not drafted
players = [x for x in raw if x.get('salary') and x['stats']]
# Sort players in descending order based on fantasyPoints
players = sorted(players, key=lambda x: x['fantasyPoints'], reverse=True)

for player in players:
    # Create fpts_salary (int:quotient of fantasyPoints and salary) element for each player (dict)
    fpts_salary = player['fantasyPoints'] / player['salary']
    player.update({"fpts_salary": fpts_salary})

    # Create a fullName element for each player by combining firstName (string) and lastName (string)
    fullName = player['firstName']
    if player['lastName']:
        fullName += ' {}'.format(player['lastName'])
        
    player.update({"fullName": '{} {}'.format(player['firstName'], player['lastName'])})

# Create a list (bust_players) of dicts where salary is greater than or equal to 5000
bust_players = [x for x in players if x.get('salary') >= 5000]

# MVP is the player with the most fantasyPoints
# Sleeper is the player with the most fpts_salary (see previously added element)
# Bust is the player with the least fpts_salary from bust_players list (see previously created list)
mvp = max(players, key=lambda x: x['fantasyPoints'])
sleeper = max(players, key=lambda x: x['fpts_salary'])
bust = min(bust_players, key=lambda x: x['fpts_salary'])

mvp_draft = []
sleeper_draft = []
bust_draft = []
users = []
drafted = set()

with open(results_file) as csv_file:
    # Use only the first 6 fields of csv_file to create a list (lines)
    for line in csv_file:
        lines = line.split(',')[:6]

        # Add entries users list containing user and user_pts as a string
        if lines[0] and lines[0] != 'Rank':
            user_name = lines[2]
            user_pts = lines[4]
            users.append("{} - {} fpts".format(user_name, user_pts))

        # Add list of users whose teams contain a player to the specified lists
        if lines[0] and mvp['fullName'] in lines[5]:
            mvp_draft.append(lines[2])
        if lines[0] and sleeper['fullName'] in lines[5]:
            sleeper_draft.append(lines[2])
        if lines[0] and bust['fullName'] in lines[5]:
            bust_draft.append(lines[2])
        
        # Add drafted players to drafted set
        # Create draft (list) by splitting each lines[5], omitting positions (QB, RB, etc.)
        # Add each draft_player (item) from draft (list) to drafted (set), while trimming (strip()) whitespace
        if lines[5] != 'Lineup' and lines[5]:
            draft = re.split('QB| RB | WR | TE | FLEX | DST ', lines[5])
            for draft_player in draft:
                if draft_player != '':
                    drafted.add(draft_player.strip())

# Create alphabetical list of user_pts
sorted_list = sorted(users, key=str.casefold)
i = 0
for x in sorted_list:
    sorted_list[i] = x.split()[2]
    i += 1

# Find top undrafted player (draft_dodger), players list is sorted by highest fantasyPoints
find_undrafted = []
for player in players:
    if player['fullName'] not in drafted:
        find_undrafted.append(player)

draft_dodger = find_undrafted[0]

# Function used to display 'Drafted by' list or 'Undrafted'
def draft_string(my_list):
    if my_list:
        members = ', '.join(my_list)
        return 'Drafted by <span class="font-weight-bold">{}</span>'.format(members)
    else:
        return '<span class="font-weight-bold">Undrafted</span>'

# Function used to create a string (filename) used to rename player screenshots
def png_name(player):
    filename = 'week-' + week + '-'
    filename += '-'.join(player.split())
    filename += '.png'
    return filename.lower()

# Compose ordered list HTML string of winners (users[:3])
winner_str = '<ol>\n'
for user in users[:3]:
    winner_str += '\t<li>{}</li>\n'.format(user)
winner_str += '</ol>'

# Write winner_str to file (results_output)
with open('2019-week-'+ week + '.html', 'w+') as results_output:
    results_output.write(winner_str)

# Replace placeholders in weekly-template with values listed below
with open('weekly-template.md', 'r') as weekly_template:
    with open(today + '-week-' + week+ '-results.md', 'w+') as weekly_output:
        template_str = weekly_template.read()
        weekly_output.write(template_str.format(
            bust_draft=draft_string(bust_draft), 
            bust_png=png_name(bust['fullName']),
            bye_teams=bye_teams,
            contest_id=contest_id,
            draft_dodger_png=png_name(draft_dodger['fullName']),
            mvp_draft=draft_string(mvp_draft),
            mvp_png=png_name(mvp['fullName']),
            sleeper_draft=draft_string(sleeper_draft),
            sleeper_png=png_name(sleeper['fullName']),
            week=week)
        )

# Output useful data on the command line
print("Points (in alphabetical order):\n", '\n'.join(sorted_list), sep='')

print("\nMVP: ", mvp['fullName'])
print("Sleeper: ", sleeper['fullName'])
print("Bust: ", bust['fullName'])
print("Draft Dodger: ", draft_dodger['fullName'])

print("\nWinners:\n", '\n'.join(users[:3]), sep='')