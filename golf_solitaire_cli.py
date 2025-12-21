from golf_solitaire import GolfGame
from typing import Callable, Dict, Any
import re
import os

state = "running"
command_list =[
    "List of commands",
    "D [1-7]: Draw the top card from said pile",
    "S:       Draw a card from the stock pile",
    "H:       List all commands",
    "U:       Undo last move",
    "X:       Exit the program"
    "R:       Restart game",
]

FACE_MAPPING = {
    "H": "♡",
    "S": "♠",
    "C": "♣",
    "D": "♢"
}
CommandFunc = Callable[[str], str]
pattern = re.compile(r"^(D\s+([1-7]))|(H)|(S)|(U)|(X)|(R)$", re.I)

def clear_screen():
    # Clear the terminal screen based on the operating system
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux, macOS
        os.system('clear')
game = GolfGame()

def handle_draw(value: str) -> str:
    col_index = int(value) - 1
    return game.try_draw_card(col_index)

def handle_hit(_value: str) -> str:
    return game.draw_from_wastepile()

def handle_help(_value: str) -> str:
    return "\n".join(command_list)

def handle_undo(_value: str)-> str:
    return game.undo()

def handle_exit(_value: str) -> str:
    global state
    state = "exit"
    return "Exiting game"

def handle_restart(_value: str) -> str:
    global game
    game = GolfGame()
    return "Restart"

command_map: Dict[str, CommandFunc] = {
        'D': handle_draw,
        'S': handle_hit,
        'H': handle_help,
        'U': handle_undo,
        'X': handle_exit,
        'R': handle_restart,
    }

def handle_parse(command_string: str) -> str:
    match = pattern.match(command_string.strip())

    if not match:
        return f"❌ ERROR: Invalid command format: '{command_string.strip()}'"

    # Determine which command was matched (Groups 1-4)
    elif match.group(2): # D [1-7] was matched
        command_type = 'D'
        command_value = match.group(2) # The number [1-7]
    elif match.group(3): # H was matched
        command_type = 'H'
        command_value = ''
    elif match.group(4): # S was matched
        command_type = 'S'
        command_value = ''
    elif match.group(5): # U was matched
        command_type = 'U'
        command_value = ''
    elif match.group(6):
        command_type = 'X'
        command_value = ''
    elif match.group(7):
        command_type = 'R'
        command_value = ''
    else:
        # Should be unreachable given the regex pattern
        return "❌ ERROR: Parsing error."
    # Execute the mapped function
    action_func = command_map[command_type]
    return action_func(command_value)
    
result: str = ""
while state != "exit":
    state = game.check_game_state()
    if state == "win":
        result = "You've won! Press (R) to play again"
    elif state == "lose":
        result = "You've lost! Press (R) to play again"
    clear_screen()
    print(game.draw_self())
    print(result)
    print()
    choice: str = input("Make your move. Press H for help\n")
    result = handle_parse(choice)