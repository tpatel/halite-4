from kaggle_environments.envs.halite.helpers import *

from random import choice


turn = 0


def score(turn, board):
    me = board.current_player

    base = 1000 if len(me.shipyards) > 1 else 0
    ships = len(me.ships) * 500
    potential_halite = sum(map(lambda ship: ship.halite, me.ships)) * 0.1
    halite = me.halite * turn / 300

    return base + ships + potential_halite + halite


def randomMoves(turn, board):
    me = board.current_player

    if turn == 0:
        me.ships[0].next_action = ShipAction.CONVERT
    else:
        for ship in me.ships:
            ship.next_action = choice(ShipAction.moves() + [None])

    for shipyard in me.shipyards:
        if me.halite > 1000:
            shipyard.next_action = choice([ShipyardAction.SPAWN, None])

    return me.next_actions.copy()


def agent(obs, config):
    global turn
    board = Board(obs, config)
    options = []

    for _ in range(50):
        next_actions = randomMoves(turn, board)
        next_score = score(turn, board.next())
        options += [(next_score, next_actions)]

    options.sort(key=lambda x: x[0], reverse=True)

    turn = turn + 1
    return options[0][1]
