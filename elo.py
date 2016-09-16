# ELO
# python 3.4.3
# Copyright (c) 2016 by Matt Sewall.
# All rights reserved.
import math
from elo_classes import *

# Background information - https://en.wikipedia.org/wiki/Elo_rating_system
# Based on this equation - http://elo-norsak.rhcloud.com/index.php

_MAXSIZE = 186
_MINBUFFEREDELO = 1900
_MAXBUFFEREDELO = 3200
_KMAX = 4.4
_BUFFEREDELOSLOPE = -.14 / 1300
_EXPODENTIALRATE = 800
_WIN = 1.0
_LOSS = 0.0


def calculateElo(players):
    N = len(players)
    # compare every head to head matchup in given competition
    for i in players:
        # changing K multiplier depending on the size of the competition
        if N > _MAXSIZE:
            K = 1.2
        else:
            k_slope = 3 * N / 175
            K = _KMAX - k_slope
        # Players with higher elo receive lower K values for stability
        multi = 1
        if i.elo > _MINBUFFEREDELO and i.elo < _MAXBUFFEREDELO:
            multi = _WIN + (_BUFFEREDELOSLOPE) * (i.elo - _MINBUFFEREDELO)
        K = multi * K
        for j in players:
            if i is not j:
                # S is the player's actual score - 1 for win - 0 for loss
                if i.place < j.place:
                    S = _WIN
                else:
                    S = _LOSS
                change = j.elo - i.elo
                # Expected is the expected score based off each players elo
                expected_score = 1 / \
                    (1.0 + math.pow(10.0, (change) / _EXPODENTIALRATE))
                i.elo += K * (S - expected_score)
        # Making zero be the rating system's floor (optional)
        if i.elo < 0:
            i.elo = 0
