import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Game.game import Game

COMMANDS = [
    ("look / l",        "Look around the room"),
    ("go [direction]",  "Move north, south, east, or west"),
    ("take [item]",     "Pick up an item"),
    ("use [item]",      "Use a consumable item"),
    ("equip [item]",    "Equip an item"),
    ("unequip [slot]",  "Unequip an item from a slot"),
    ("examine [x]",     "Examine an item or enemy"),
    ("inventory / i",   "Check your inventory"),
    ("stats / s",       "Check your stats"),
    ("attack [enemy]",  "Attack an enemy"),
    ("help / h",        "Show this list again"),
    ("quit / q",        "Quit the game"),
]

def print_startup():
    width = 62
    heavy = "+" + "=" * (width - 2) + "+"
    print(heavy)
    print("|" + " D E S C E N T ".center(width - 2) + "|")
    print("|" + "A Text-Based Adventure".center(width - 2) + "|")
    print(heavy)
    print()
    print("Commands:")
    for cmd, desc in COMMANDS:
        print(f"  {cmd:<18} {desc}")
    print()
    print(heavy)
    print()

def show_end_screen(game):
    width = 62
    heavy = "+" + "=" * (width - 2) + "+"
    print()
    print(heavy)
    if game.outcome == 'win':
        print("|" + "ELIGOR HAS BEEN VANQUISHED".center(width - 2) + "|")
        print("|" + "Light returns to the depths.".center(width - 2) + "|")
    else:
        print("|" + "YOU HAVE FALLEN".center(width - 2) + "|")
        print("|" + "The darkness claims your soul...".center(width - 2) + "|")
    print(heavy)
    print()
    print(f"  Level reached    : {game.player.level}")
    print(f"  Enemies defeated : {game.enemies_defeated}")
    print(f"  Experience       : {game.player.experience}")
    print()
    while True:
        choice = input("  Play again? (yes / no) : ").strip().lower()
        if choice in ['yes', 'y']:
            return True
        if choice in ['no', 'n']:
            return False
        print("  Please enter 'yes' or 'no'.")


def main():
    while True:
        game = Game()
        game.load_world()
        loaded = False
        # List all files that could be saves: .json files and files with no extension
        save_files = [f for f in os.listdir('.') if os.path.isfile(f) and (f.endswith('.json') or '.' not in f)]
        if save_files:
            print("  Available save files:")
            for f in save_files:
                print(f"    - {f}")
            choice = input("  Load a save file? (yes / no) : ").strip().lower()
            if choice in ['yes', 'y']:
                filename = input("  Enter save file name (default: save.json): ").strip()
                if not filename:
                    filename = 'save.json'
                if not os.path.exists(filename):
                    print(f"  File '{filename}' not found. Starting new game.")
                else:
                    try:
                        game.load(filename)
                        print(f"  Game loaded from {filename}.")
                        loaded = True
                    except Exception as e:
                        print(f"  Failed to load save: {e}")
        if not loaded:
            name = input("Enter your name, brave adventurer: ").strip()
            if not name:
                name = "Hero"
            game.player.name = name
        print_startup()
        print(game.player.current_room.describe())
        print()

        while game.running:
            command = input("> ").strip()
            if command.lower() in ['quit', 'q']:
                print("Thanks for playing!")
                game.running = False
            else:
                result = game.process_command(command)
                if result:
                    print(result)
                print()

        if game.outcome in ('win', 'death'):
            if not show_end_screen(game):
                break
        else:
            break  # quit command

if __name__ == '__main__':
    main()