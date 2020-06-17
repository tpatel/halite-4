from kaggle_environments.envs.halite.helpers import *

from random import choice

turn = 0


def agent(obs, config):
    global turn
    board = Board(obs, config)
    me = board.current_player

    if turn == 0:
        me.ships[0].next_action = ShipAction.CONVERT
    else:
        for ship in me.ships:
            ship.next_action = choice(ShipAction.moves() + [None])

    for shipyard in me.shipyards:
        if me.halite > 1000:
            shipyard.next_action = ShipyardAction.SPAWN

    turn = turn + 1
    return me.next_actions
