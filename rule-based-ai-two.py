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


def agent(obs, config):
    global turn
    global configuration
    configuration = config
    board = Board(obs, config)
    me = board.current_player
    remaining_halite = me.halite

    moved_to = set({})
    moved = set({})

    if turn == 0:
        me.ships[0].next_action = ShipAction.CONVERT
    else:
        # Find the halite that is not too far away from one base and that has the most halite
        # Only spots that have more than x halite
        halite_spots = list(filter(lambda cell: cell.halite > 300 and min(list(map(
            lambda shipyard: distance(shipyard.position, cell.position), me.shipyards)) + [400]) < 10, board.cells.values()))

        halite_spots.sort(key=lambda cell: cell.halite)

        for ship in me.ships:
            if ship.halite > 1500:
                moved.add(ship.id)
                ship.next_action = ShipAction.CONVERT
            elif ship.halite > 500 and len(me.shipyards) > 0:
                me.shipyards.sort(
                    key=lambda shipyard: distance(shipyard.position, ship.position))
                next_action = move_to(
                    ship.position, me.shipyards[0].position)

                # Avoid collisions
                if next_action[1] not in moved_to:
                    moved_to.add(next_action[1])
                    moved.add(ship.id)
                    ship.next_action = next_action[0]

        # Assign one halite spot to each ship
        # Make the ship stay on the halite spot
        # If not already there, make the ship move to the assigned halite spot
        for cell in halite_spots:
            available_ships = list(
                filter(lambda ship: ship.id not in moved, me.ships))
            available_ships.sort(key=lambda ship: distance(
                cell.position, ship.position))

            if len(available_ships) > 0:
                ship = available_ships[0]
                if ship.position == cell.position:
                    moved.add(ship.id)
                    moved_to.add(cell.position)
                else:
                    next_action = move_to(
                        ship.position, cell.position)

                    # Avoid collisions
                    if next_action[1] not in moved_to:
                        moved_to.add(next_action[1])
                        moved.add(ship.id)
                        ship.next_action = next_action[0]
                    else:
                        print('Unused ship')

    # create more shipyards
    for kami in me.shipyards:
        empty_shipyard = board[kami.position].ship == None and kami.position not in moved_to

        if empty_shipyard and remaining_halite >= 500:
            kami.next_action = ShipyardAction.SPAWN
            if kami.next_action == ShipyardAction.SPAWN:
                remaining_halite -= 500

    turn = turn + 1
    return me.next_actions