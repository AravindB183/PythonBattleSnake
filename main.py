import random
import typing
from typing import List, Dict

# Monty uses floodfill to predict safe moves one turn ahead and the manhattan distance 
# algorithm to determine the shortest path to food when it detects its at half health

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "monty",  # TODO: Your Battlesnake Username
        "color": "#6600cc",  # TODO: Choose color
        "head": "pixel",  # TODO: Choose head
        "tail": "pixel",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")

# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

def avoid_my_body(my_body, is_move_safe):
  remove = []
  for direction, location in is_move_safe.items():
    if location in my_body:
      remove.append(direction)

  for direction in remove:
    del is_move_safe[direction]

  return is_move_safe

def avoid_snakes(opponents, is_move_safe):
  remove = []
  for opponent in opponents:
    for direction, location in is_move_safe.items():
      if location in opponent["body"]:
        remove.append(direction)

  for direction in remove:
    del is_move_safe[direction]

  return is_move_safe

def avoid_walls(board_width: Dict[str, int], board_height: List[dict], is_move_safe: List[str]) -> List[str]:
    remove = []

    for direction, location in is_move_safe.items():
        x_out_range = (location["x"] < 0 or location["x"] >= board_width)
        y_out_range = (location["y"] < 0 or location["y"] >= board_height)
        if x_out_range or y_out_range:
            remove.append(direction)

    for direction in remove:
        del is_move_safe[direction]

    return is_move_safe

# search for food
def get_closest_target(targets, my_head):
   if not targets:
      return None
   closest_target = min(targets, key=lambda target: abs(target["x"] - my_head["x"]) + abs(target["y"] - my_head["y"]))
   return closest_target

def move_target(safe_moves, my_head, target):
   next_move = None
   min_distance = float("inf")

   for move in safe_moves:
      if move == "up":
         new_position = {"x": my_head["x"], "y": my_head["y"] + 1}
      elif move == "down":
         new_position = {"x": my_head["x"], "y": my_head["y"] - 1}
      elif move == "left":
         new_position = {"x": my_head["x"] - 1, "y": my_head["y"]}
      elif move == "right":
         new_position = {"x": my_head["x"] + 1, "y": my_head["y"]}

      distance = abs(new_position["x"] - target["x"]) + abs(new_position["y"] - target["y"])

      if distance < min_distance:
         next_move = move
         min_distance = distance

   return next_move

def flood_fill(board, start_x, start_y):
   stack = [(start_x, start_y)]
   safe_area = {(start_x, start_y)}

   while stack:
      x, y = stack.pop()
      for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
         nx, ny = x + dx, y + dy
         if 0 <= nx < board["width"] and 0 <= ny < board["height"] and (nx, ny) not in safe_area and not is_collision(board, nx, ny):
            stack.append((nx, ny))
            safe_area.add((nx, ny))

   return safe_area
         
def is_collision(board, x, y):
    # check if (x, y) collides with snake body
    for snake in board["snakes"]:
       for body_part in snake["body"]:
          if body_part["x"] == x and body_part["y"] == y:
             return True
    # check if (x, y) collides with walls
    if x < 0 or y < 0 or x >= board["width"] or y>= board["height"]:
       return True
    return False

def opponent_moves(opponent_head):
   x, y = opponent_head["x"], opponent_head["y"]
   return ["up", "down", "left", "right"]
            

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_body = game_state['you']['body']
  
    board = game_state['board']
    my_health = game_state["you"]["health"]

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
  
    opponents = game_state['board']['snakes']
  
    # determine the health threshold to start searching for food
    half_health = board["height"] * board["width"] // 2



    is_move_safe = {
      "up": True, 
      "down": True, 
      "left": True, 
      "right": True
    }

    is_move_safe = {
      "up": {
        "x": my_head["x"],
        "y": my_head["y"] +1,
      },
      "down": {
        "x": my_head["x"],
        "y": my_head["y"] -1,
      },
      "left": {
        "x": my_head["x"] -1,
        "y": my_head["y"],
      },
      "right": {
        "x": my_head["x"] +1,
        "y": my_head["y"],
      },
    }

    is_move_safe = avoid_my_body(my_body, is_move_safe)
    is_move_safe = avoid_snakes(opponents, is_move_safe)
    is_move_safe = avoid_walls(board_width, board_height, is_move_safe)

    # if health is below the threshold, prioritize finding food
    if my_health <= half_health:
       # find the closest food
       closest_food = get_closest_target(board["food"], my_head)

       if closest_food:
        # get the safe area reachable using floodfill
        safe_area = flood_fill(board, my_head["x"], my_head["y"])
        safe_moves_to_food = [move for move in ["up", "down", "left", "right"] if move == "up" and (my_head["x"], my_head["y"] + 1) in safe_area or
                                                                                                    (move == "down" and (my_head["x"], my_head["y"] - 1) in safe_area) or
                                                                                                    (move == "left" and (my_head["x"] - 1, my_head["y"]) in safe_area) or
                                                                                                    (move == "right" and (my_head["x"] + 1, my_head["y"]) in safe_area)]
                                                                                
        if safe_moves_to_food:
           next_move = move_target(safe_moves_to_food, my_head, closest_food)
           print(f"MOVE {game_state['turn']}: {next_move} (Seeking food)")
           return {"move": next_move}

    # if not seeking food or no safe moves towards food, determine the safest move
    # get the safe are reachable from the head position using floodfill
    safe_area = flood_fill(board, my_head["x"], my_head["y"])
    safe_moves = [move for move in ["up", "down", "left", "right"] if (move == "up" and (my_head["x"], my_head["y"] + 1) in safe_area) or
                                                                    (move == "down" and (my_head["x"], my_head["y"] - 1) in safe_area) or
                                                                    (move == "left" and (my_head["x"] - 1, my_head["y"]) in safe_area) or
                                                                    (move == "right" and (my_head["x"] + 1, my_head["y"]) in safe_area)]
    
  
    if safe_moves:
       safest_move = move_target(safe_moves, my_head, my_head)
       print(f"MOVE {game_state['turn']}: {safest_move}")
       return {"move": safest_move}
    else:
        # no safe moves detected
        print(f"MOVE {game_state['turn']}: No safe moves detected, moving down")
        return {"move": "down"}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({
        "info": info, 
        "start": start, 
         "move": move, 
        "end": end
    })
