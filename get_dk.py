#! /usr/bin/python3

import requests

# Capture user input to assign values to week
week = str(input('2019 NFL Week #: '))
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

print(dk_resp.text)