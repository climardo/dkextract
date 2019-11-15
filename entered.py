#! /usr/bin/python3

import argparse

parser = argparse.ArgumentParser(description='Process a file to see who hasn\'t entered')
parser.add_argument('filename', metavar='file', type=str, nargs=1,
                    help='The absolute or relative path to the file being processes')

args = parser.parse_args()
filename = args.filename[0]

entered = []
all_users = ['albythealbanian', 'arianna29', 'BrunoDiaz', 'C-Bail', 'climardo', 'DarbyDiaz3', 'Dash7', 'ejmesa', 'frank.corn', 'glopez28', 'Halvworld', 'hlimardo', 'JekellP', 'jlopez0809', 'LoLoGREEN', 'olivadotij', 'pshhidk', 'rogdiaz', 'XplicitK']

with open(filename) as file1:
    lines = []
    for x in file1:
        lines.append(x.split())
    for x in lines:
        if len(x) > 1:
            n1 = x[3].split('>')
            n2 = n1[1].split('<')
            user_name = n2[0]
            entered.append(user_name)

unsubmitted = set(all_users) - set(entered)
print(unsubmitted)