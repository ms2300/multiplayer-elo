class ELOPlayer:
    def __init__(self, name, school, place, eloPre):
        self.name = name
        self.school = school
        self.place = place
        self.eloPre = eloPre
    eloPost = None
    eloChange = 0

    def __eq__(self, other):
        return self.name == other.name and \
               self.school == other.school

    def __hash__(self):
        return hash((self.name, self.school))


# used to find unique athletes
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


# in conjunction with ELOPlayer
# calculates elo
class Meet:
    players = []

    def addPlayer(self, name, place, elo, school):
        player = ELOPlayer(name, school, place, elo)
        self.players.append(player)
