# ELO
# python 3.4.3
import math
import csv
import json
import os
import shutil
from sys import argv
from datetime import datetime
from django.utils.encoding import smart_str, smart_unicode
from operator import itemgetter
from elo_classes import *

# Background information - https://en.wikipedia.org/wiki/Elo_rating_system
# Based on this equation - http://elo-norsak.rhcloud.com/index.php

# Elos dictionaries contain athletes keyed to an elo value
# Entries dictionaries contain athletes keyed to history of their results

elos_boys = {}
elos_girls = {}
entries_boys = {}
entries_girls = {}
_MAXSIZE = 186
_MINBUFFEREDELO = 1900
_MAXBUFFEREDELO = 3200
_YMAX = 4.4
_BASE = 1
_BUFFEREDELOSLOPE = -.14 / 1300
_EXPODENTIALRATE = 800
_DEFELO = 1500.0


def calculateELOs(players):
    N = len(players)
    # compare every head to head matchup in given meet
    for i in players:
        curPlace = i.place
        curELO = i.eloPre
        # changing K multiplier depending on the size of race
        # K multiplier is maximum amount points that can be gained from a win
        if N > _MAXSIZE:
            K = 1.2
        else:
            k_slope = 3 * N / 175
            K = _YMAX - k_slope
        # chaning K multiplier depending on elo of runner
        multi = 1
        if curELO > _MINBUFFEREDELO and curELO < _MAXBUFFEREDELO:
            multi = _BASE + (_BUFFEREDELOSLOPE) * (curELO - _MINBUFFEREDELO)
        K = multi * K
        for j in players:
            if i is not j:
                opponentPlace = j.place
                opponentELO = j.eloPre
                # S is the player's score - 1 for win - 0 for loss
                if curPlace < opponentPlace:
                    S = 1.0
                elif curPlace == opponentPlace:
                    S = 0.5
                else:
                    S = 0.0
                change = opponentELO - curELO
                # EA is the expected probability of player winning
                EA = 1 / (1.0 + math.pow(10.0, (change) / _EXPODENTIALRATE))
                i.eloChange += K * (S - EA)
        i.eloPost = i.eloPre + i.eloChange
        # making it so zero is floor of elo rating
        if i.eloPost < 0:
            i.eloPost = 0


def do_elo(data, meetName, meetDate, gender):
    meet = Meet()
    meet.players = []
    if gender == "female":
        elos = elos_girls
        entries = entries_girls
    elif gender == "male":
        elos = elos_boys
        entries = entries_boys
    for dat in data:
        name = dat[0]
        place = int(dat[1])
        school = dat[2]
        ath = Athlete(name, school)
        if ath in elos:
            elo = float(elos.get(ath))
            meet.addPlayer(name, place, elo, school)
        else:
            # defaults to elo of 1500 on athletes first meet
            meet.addPlayer(name, place, _DEFELO, school)
    calculateELOs(meet.players)
    for runner in meet.players:
        ather = Athlete(runner.name, runner.school)
        elos[ather] = runner.eloPost
        if ather in entries:
            res_list = entries.get(ather)
            res_list.append([meetName, meetDate, runner.eloPost])
            entries[ather] = res_list
        else:
            entries[ather] = [[meetName, meetDate, runner.eloPost]]


def align_data(filename):
    filex = open(filename)
    sort = []
    for json_string in filex:
        parsed = json.loads(json_string)
        results = parsed["results"]
        kill = False
        locs = parsed["meetLocation"]
        a_date = parsed["meetDate"]
        exact_date = datetime.strptime(a_date[0], "%A, %B %d, %Y")
        for loc in locs:
            if loc == u'Collegiate' or loc == u'MS':
                kill = True
        for result in results:
            if result.keys() == [u'maleResults'] or [u'femaleResults']:
                static = result.values()
                events = static[0]
                for event in events:
                    data = []
                    data.append(exact_date)
                    data.append(parsed['meetName'])
                    if result.keys() == [u'maleResults']:
                        data.append("male")
                    elif result.keys() == [u'femaleResults']:
                        data.append("female")
                    places = []
                    details = event[u'eventDetails']
                    for detail in details:
                        killx = False
                        ath_detail_List = []
                        ath_detail_List.append(
                                        smart_str(detail[u'resultName']))
                        if detail[u'resultPlace'] == " " or \
                                detail[u'resultPlace'] == u' ':
                            killx = True
                        else:
                            ath_detail_List.append(detail[u'resultPlace'])
                        ath_detail_List.append(
                                        smart_str(detail[u'resultSchool']))
                        if killx is False:
                            places.append(ath_detail_List)
                    data.append(places)
                    if kill is False:
                        sort.append(data)
    sortx = sorted(sort, key=itemgetter(0))
    return sortx


def write_ath(entries):
    if entries == entries_boys:
        path = "./meets/boys"
    elif entries == entries_girls:
        path = "./meets/girls"
    if not os.path.exists("./meets/"):
        os.mkdir("./meets/")
    if not os.path.exists(path):
        os.mkdir(path + "/")
    for ath in entries:
        school_path = os.path.join(path, ath.school)
        ath_path = os.path.join(school_path, ath.name + ".csv")
        filename = "%s.csv" % ath.name
        with open((filename), "w") as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(entries[ath])
        if os.path.exists(school_path):
            shutil.move(filename, ath_path)
        else:
            os.mkdir(school_path)
            shutil.move(filename, ath_path)


def write_elo(elos, gender):
    if gender == "male":
        name = "athlete_elo_boys.csv"
    elif gender == "female":
        name = "athlete_elo_girls.csv"
    with open((name), "w") as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(elos)


def main():
    # isolates every event and pass that into the do_elo function by gender
    events = align_data(argv[1])
    for event in events:
        # makes sure there are 4 values of (name, date, gender, and results)
        if len(event) == 4:
            name = smart_str(event[1][0])
            date = event[0]
            gender = event[2]
            do_elo(event[3], name, date, gender)
    # sorts the dictionaries by ascending elo
    sorted_boys = sorted(elos_boys.items(), key=itemgetter(1))
    sorted_girls = sorted(elos_girls.items(), key=itemgetter(1))
    write_elo(sorted_boys, "male")
    write_elo(sorted_girls, "female")
    write_ath(entries_girls)
    write_ath(entries_boys)


if __name__ == '__main__':
    main()
