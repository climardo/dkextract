#! /usr/bin/python3

import json, argparse, re, requests
from datetime import datetime

parser = argparse.ArgumentParser(description='Process a JSON file from live.draftkings.com and contest results CSV to output data for provided week')
parser.add_argument('week', metavar='week', type=int, nargs=1,
                    help='NFL season week #')
parser.add_argument('filename', metavar='file', type=str, nargs=2,
                    help='The absolute or relative path to the files being processes')

args = parser.parse_args()
weekly_file = args.filename[0]
results_file = args.filename[1]
week = str(args.week[0])
today = datetime.now().strftime('%Y-%m-%d')

# Get contest_id (string) from results_file (string), assuming it exists just before extension (default)
results_file_splt = re.split('/|-|\.',results_file)
contest_id = results_file_splt[len(results_file_splt) - 2]

# Get list of bye_teams by downloading and parsing data from Yahoo Sports
get_game_data = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues=nfl&week={}&season=current'.format(week)
r = requests.get(url=get_game_data)
game_data = r.json()['service']['scoreboard']
bye_teams_raw = set(game_data['bye_teams'])
bye_teams = []
for team in game_data['teams']:
    if team in bye_teams_raw:
        bye_teams.append(game_data['teams'][team]['full_name'])
bye_teams = ', '.join(bye_teams)

with open(weekly_file) as json_file:
    '''
    Parse the file (weekly_file) to get a dict using json
    Use the resulting dict (raw) and filter players that have a salary and stats
    This creates a list (players) containing dicts
    '''
    raw = json.load(json_file).get('data')
    players = [x for x in raw if x.get('salary') and x['stats']]
    players = sorted(players, key=lambda x: x['fantasyPoints'], reverse=True)

# Add an element to each dict (player) which is contains a quotient (fpts_salary)
for player in players:
    fpts_salary = player['fantasyPoints'] / player['salary']
    player.update({"fpts_salary": fpts_salary})

    fullName = player['firstName']
    if player['lastName']:
        fullName += ' {}'.format(player['lastName'])
        
    player.update({"fullName": '{} {}'.format(player['firstName'], player['lastName'])})

# Create a list (bust_players) of dicts where salary is greater than or equal to 5000
bust_players = [x for x in players if x.get('salary') >= 5000]

'''
MVP is the player with the most fantasyPoints
Sleeper is the player with the most fpts_salary (see previously added element)
Bust is the player with the least fpts_salary from bust_players list (see previously created list)
'''
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
        
        '''
        Add drafted players to drafted set
        Create draft (list) by splitting each lines[5], omitting positions (QB, RB, etc.)
        Add each draft_player (item) from draft (list) to drafted (set), while trimming (strip()) whitespace
        '''
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