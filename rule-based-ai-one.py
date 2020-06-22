from kaggle_environments.envs.halite.helpers import *
import json
from random import choice

turn = 0
configuration = None

# disclaimer: some variable names where changed while on Twitch so it might look funny :) https://twitch.tv/thibpat


def distance(p1: Point, p2: Point):
    global configuration
    return min(abs(p1.x-p2.x), configuration.size - abs(p1.x-p2.x)) + min(abs(p1.y-p2.y), configuration.size - abs(p1.y-p2.y))


def move_to(fromPosition: Point, toPosition: Point):
    global configuration
    if abs(fromPosition.x-toPosition.x) < configuration.size - abs(fromPosition.x-toPosition.x):
        if fromPosition.x < toPosition.x:
            return (ShipAction.EAST, Point(fromPosition.x+1, fromPosition.y))
        if fromPosition.x > toPosition.x:
            return (ShipAction.WEST, Point(fromPosition.x-1, fromPosition.y))
    else:
        if fromPosition.x < toPosition.x:
            return (ShipAction.WEST, Point(fromPosition.x-1, fromPosition.y))
        if fromPosition.x > toPosition.x:
            return (ShipAction.EAST, Point(fromPosition.x+1, fromPosition.y))

    if abs(fromPosition.y-toPosition.y) < configuration.size - abs(fromPosition.y-toPosition.y):
        if fromPosition.y < toPosition.y:
            return (ShipAction.NORTH, Point(fromPosition.x, fromPosition.y+1))
        if fromPosition.y > toPosition.y:
            return (ShipAction.SOUTH, Point(fromPosition.x, fromPosition.y-1))
    else:
        if fromPosition.y < toPosition.y:
            return (ShipAction.SOUTH, Point(fromPosition.x, fromPosition.y-1))
        if fromPosition.y > toPosition.y:
            return (ShipAction.NORTH, Point(fromPosition.x, fromPosition.y+1))

# This AI is just rushing the nearby shipyards


def agent(obs, config):
    global turn
    global configuration
    configuration = config
    board = Board(obs, config)
    me = board.current_player
    remaining_halite = me.halite

    moved_to = set({})

    opponent_shipyards = list(filter(
        lambda kami: kami.player.id != me.id, board.shipyards.values()))

    if turn == 0:
        me.ships[0].next_action = ShipAction.CONVERT
    else:
        for ship in me.ships:
            if(len(opponent_shipyards) > 0):
                # find the closest opponent shipyard
                opponent_shipyards.sort(key=lambda kami: distance(
                    kami.position, ship.position))
                # ship needs to move closer to opponent_shipyards[0]
                next_action = move_to(
                    ship.position, opponent_shipyards[0].position)
                if next_action[1] not in moved_to:
                    moved_to.add(next_action[1])
                    ship.next_action = next_action[0]

    for kami in me.shipyards:
        # todo: make sure we don't already have a ship on the shipyard
        empty_shipyard = board[kami.position].ship == None and kami.position not in moved_to

        if empty_shipyard and remaining_halite >= 500:
            kami.next_action = ShipyardAction.SPAWN
            if kami.next_action == ShipyardAction.SPAWN:
                remaining_halite -= 500

    turn = turn + 1
    return me.next_actions
