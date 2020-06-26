from kaggle_environments.envs.halite.helpers import *
import json
from random import choice

turn = 0
configuration = None

# disclaimer: some variable names where changed while on Twitch so it might look funny :) https://twitch.tv/thibpat


def distance(p1: Point, p2: Point):
    global configuration
    return min(abs(p1.x-p2.x), configuration.size - abs(p1.x-p2.x)) + min(abs(p1.y-p2.y), configuration.size - abs(p1.y-p2.y))


def next_position_from_action(position: Point, action: ShipAction):
    global configuration
    if action == ShipAction.CONVERT or action == None:
        return Point(position.x, position.y)
    if action == ShipAction.EAST:
        return Point(position.x+1 if position.x+1 < configuration.size else 0, position.y)
    if action == ShipAction.WEST:
        return Point(position.x-1 if position.x-1 >= 0 else configuration.size-1, position.y)
    if action == ShipAction.NORTH:
        return Point(position.x, position.y+1 if position.y+1 < configuration.size else 0)
    if action == ShipAction.SOUTH:
        return Point(position.x, position.y-1 if position.y >= 0 else configuration.size)


def move_to(fromPosition: Point, toPosition: Point):
    global configuration
    if abs(fromPosition.x-toPosition.x) < configuration.size - abs(fromPosition.x-toPosition.x):
        if fromPosition.x < toPosition.x:
            return (ShipAction.EAST, next_position_from_action(fromPosition, ShipAction.EAST))
        if fromPosition.x > toPosition.x:
            return (ShipAction.WEST, next_position_from_action(fromPosition, ShipAction.WEST))
    else:
        if fromPosition.x < toPosition.x:
            return (ShipAction.WEST, next_position_from_action(fromPosition, ShipAction.WEST))
        if fromPosition.x > toPosition.x:
            return (ShipAction.EAST, next_position_from_action(fromPosition, ShipAction.EAST))

    if abs(fromPosition.y-toPosition.y) < configuration.size - abs(fromPosition.y-toPosition.y):
        if fromPosition.y < toPosition.y:
            return (ShipAction.NORTH, next_position_from_action(fromPosition, ShipAction.NORTH))
        if fromPosition.y > toPosition.y:
            return (ShipAction.SOUTH, next_position_from_action(fromPosition, ShipAction.SOUTH))
    else:
        if fromPosition.y < toPosition.y:
            return (ShipAction.SOUTH, next_position_from_action(fromPosition, ShipAction.SOUTH))
        if fromPosition.y > toPosition.y:
            return (ShipAction.NORTH, next_position_from_action(fromPosition, ShipAction.NORTH))


def agent(obs, config):
    global turn
    global configuration
    configuration = config
    board = Board(obs, config)
    me = board.current_player
    remaining_halite = me.halite

    moved_to = set({})
    moved = {}
    assigned = set({})

    danger = {}
    for opponent in board.opponents:
        for ship in opponent.ships:
            for position in (list(map(lambda action: next_position_from_action(ship.position, action), ShipAction.moves())) + [None]):
                danger[position] = min(
                    ship.halite, danger[position]) if position in danger else ship.halite
        for kami in opponent.shipyards:
            danger[kami.position] = 0

    if turn == 0:
        me.ships[0].next_action = ShipAction.CONVERT
    else:
        # Find the halite that is not too far away from one base and that has the most halite
        # Only spots that have more than x halite
        halite_spots = list(filter(lambda cell: cell.halite > 300 and min(list(map(
            lambda shipyard: distance(shipyard.position, cell.position), me.shipyards)) + [400]) < 10, board.cells.values()))

        halite_spots.sort(key=lambda cell: cell.halite)

        for ship in me.ships:
            if ship.halite > 1500 or (ship.halite > 500 and min(list(map(
                    lambda shipyard: distance(shipyard.position, ship.position), me.shipyards)) + [400]) > 4):
                # converting into a shipyard
                moved[ship.id] = ship.position
                ship.next_action = ShipAction.CONVERT

        # Assign one halite spot to each ship
        # Make the ship stay on the halite spot
        # If not already there, make the ship move to the assigned halite spot
        options = []
        for cell in halite_spots:
            for ship in me.ships:
                options += [(cell.halite*.25 - distance(ship.position,
                                                        cell.position)*10, cell.position, ship, False)]

        for ship in me.ships:
            # moving back to base
            me.shipyards.sort(
                key=lambda shipyard: distance(shipyard.position, ship.position))
            position = me.shipyards[0].position
            options += [(ship.halite - distance(ship.position,
                                                position)*10, position, ship, True)]

        options.sort(key=lambda option: option[0], reverse=True)

        for option in options:
            ship = option[2]
            position = option[1]
            is_shipyard = option[3]
            next_action = (None, ship.position)
            if ship.position != position:
                next_action = move_to(
                    ship.position, position)
            if ship.id not in moved and position not in assigned and next_action[1] not in moved_to:
                moved_to.add(next_action[1])
                moved[ship.id] = next_action[1]
                ship.next_action = next_action[0]
                if not is_shipyard:
                    assigned.add(position)

        # Avoid danger is ship has halite
        # for ship in ships:
        #     if ship.id in moved:
        #         next_position = moved[ship.id]
        #         next_position_shipyard = board.cells[next_position].shipyard
        #         if next_position_shipyard is not None:

    # create more shipyards
    for kami in me.shipyards:
        empty_shipyard = board[kami.position].ship == None and kami.position not in moved_to

        if empty_shipyard and remaining_halite >= 500 and len(me.ships) < 30:
            kami.next_action = ShipyardAction.SPAWN
            if kami.next_action == ShipyardAction.SPAWN:
                remaining_halite -= 500

    turn = turn + 1
    return me.next_actions
