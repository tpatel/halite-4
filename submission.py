from random import choice


def agent(obs):
    action = {}
    ship_id = list(obs.players[obs.player][2].keys())[0]
    ship_action = choice(["NORTH", "SOUTH", "EAST", "WEST", None])
    if ship_action is not None:
        action[ship_id] = ship_action
    return action
