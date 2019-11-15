#! /usr/bin/python3

import json, argparse

parser = argparse.ArgumentParser(description='Process a JSON file from live.draftkings.com to get some data')
parser.add_argument('filename', metavar='week-n.json', type=str, nargs=1,
                    help='The absolute or relative path to the file being processes')

parser.add_argument('-w', dest='position', metavar='[WR, QB, DEF, etc.]', type=str, nargs=1,
                    help='The player\'s position')
parser.add_argument('-s', dest='salary', metavar='5200', type=int, nargs=1,
                    help='The player\'s maximum salary')

args = parser.parse_args()
filename = args.filename[0]
position = args.position[0]
salary = args.salary[0]

with open(filename) as json_file:
    '''
    Parse the file (filename) to get a dict using json
    Use the resulting dict (raw) and filter players that have a salary
    This creates a list (players) containing dicts
    '''
    raw = json.load(json_file).get('data')
    players = [x for x in raw if x.get('salary')]

cheap = [x for x in players if x.get('salary') <= salary and x.get('position') == position]

'''
Iterate through list of players and output first and last name
Additionally, look at the player's stats
'''
for player in cheap:
    stats = player['fantasyStatsPerGame']
    for stat in stats:
        if stat.get('statId') == 467:
            avg_targets = stat.get('total')
            player.update({'avg_targets': avg_targets})
    
    print(player['firstName'], player['lastName'], player['avg_targets'])
