# Copyright (c) 2016 by Matt Sewall.
# All rights reserved.


class Competitor:
    def __init__(self, name, school, place, elo):
        self.name = name
        self.school = school
        self.place = place
        self.elo = elo

    def __eq__(self, other):
        return self.name == other.name and \
               self.school == other.school

    def __hash__(self):
        return hash((self.name, self.school))


# Used as a class for example.py, and is not relevant to the core algorithm

class Athlete:
    def __init__(self, name, school):
        self.name = name
        self.school = school

    def __eq__(self, other):
        return self.name == other.name and \
               self.school == other.school

    def __hash__(self):
        return hash((self.name, self.school))

    def __repr__(self):
        return self.name


class Meet:
    competitors = []

    def addCompetitor(self, name, place, elo, school):
        player = Competitor(name, school, place, elo)
        self.competitors.append(player)
