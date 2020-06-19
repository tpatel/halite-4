from kaggle_environments.envs.halite.helpers import *
import json
from random import choice


turn = 0


def score(turn, board):
    me = board.current_player

    base = 1000 if len(me.shipyards) > 1 else 0
    ships = len(me.ships) * 500 * (400-turn) / 400
    potential_halite = sum(map(lambda ship: ship.halite, me.ships)) * 0.1
    halite = me.halite * turn / 300

    return base + ships + potential_halite + halite


def randomMoves(turn, board):
    me = board.current_player
    remaining_halite = me.halite

    if turn == 0:
        me.ships[0].next_action = ShipAction.CONVERT
    else:
        for ship in me.ships:
            ship.next_action = choice(
                ShipAction.moves() + [None, ShipAction.CONVERT])

    for shipyard in me.shipyards:
        if len(me.ships) == 0 or remaining_halite > (1000 + turn*4):
            shipyard.next_action = choice(
                [ShipyardAction.SPAWN, None, None, None])
            if shipyard.next_action == ShipyardAction.SPAWN:
                remaining_halite -= 500

    return board.next()


def deepRandomMoves(depth, turn, board, actions):
    if depth == 0:
        return (score(turn, board), actions[0])

    options = []
    already_seen = set()

    for _ in range(5):
        next_board = randomMoves(turn, board)
        next_actions = board.current_player.next_actions
        id = json.dumps(next_actions)
        # next_score = score(turn, board.next())
        if id not in already_seen:
            # if turn < 20:
            #     print(str(score(turn, board)) + " " +
            #           str(score(turn, next_board)))
            #     print(deepRandomMoves(depth-1, turn+1, next_board,
            #                           actions.copy() + [next_actions]))
            options += [deepRandomMoves(depth-1, turn+1,
                                        next_board, actions.copy() + [next_actions])]
        already_seen.add(id)

    # if turn < 20:
    #     print(options)
    options.sort(key=lambda x: x[0], reverse=True)

    return options[0]


def agent(obs, config):
    global turn
    board = Board(obs, config)

    if(turn < 10 or turn % 50 == 0):
        print("turn " + str(turn))

    option = deepRandomMoves(2, turn, board, [])

    turn = turn + 1
    return option[1]
