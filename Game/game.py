import os
import sys
from random import random

from Models import player
from Models import enemy
from Models.player import Player
from Models.enemy import Enemy
from Systems.world_loader import WorldLoader
from Systems.combat import Combat


def _resource_path(relative_path):
    """Resolve path whether running normally or as a PyInstaller bundle."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # _MEIPASS is set by PyInstaller; otherwise use the directory of game.py
    # but we need the project root (one level up from Game/)
    if not hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(base)  # go up from Game/ to project root
    return os.path.join(base, relative_path)


class Game:
    def __init__(self):
        self.player = Player("Hero", health=100, attack=10, defense=5, speed=5, crit_chance=0.1, crit_multiplier=2)
        self.rooms = {}
        self.running = True
        self.outcome = None
        self.enemies_defeated = 0

    def load_world(self):
        loader = WorldLoader(_resource_path("Assets/Data/rooms.json"), _resource_path("Assets/Data/items.json"))
        self.rooms, self.item_catalogue = loader.load()
        self.player.current_room = self.rooms['subway_platform']

    def process_command(self, command):
        command = command.lower().strip()
        if command in ['look', 'l']:
            return self.player.current_room.describe()
        elif command.startswith('go '):
            direction = command[3:]
            current_room = self.player.current_room
            # Check if a living enemy blocks this exit
            if (current_room.enemy and current_room.enemy.is_alive
                    and direction in current_room.blocks_exits):
                return f"The {current_room.enemy.name} blocks your path to the {direction}!"
            # Peek at the destination room to check if it's locked
            dest_id = current_room.connections.get(direction)
            if dest_id:
                dest_room = self.rooms.get(dest_id)
                if dest_room and dest_room.locked:
                    required = dest_room.required_key
                    has_key = any(
                        hasattr(item, 'key_id') and item.key_id == required
                        for item in self.player.inventory
                    )
                    if not has_key:
                        return "The way is locked. You need a key to pass."
            if self.player.move(direction, self.rooms):
                print(self.player.current_room.describe())
                if self.player.current_room.enemy and self.player.current_room.enemy.is_alive:
                    print(f"A {self.player.current_room.enemy.name} appears!")
                    self.start_combat(self.player.current_room.enemy)
            else:
                return "You can't go that way."
        elif command.startswith('take '):
            item_name = command[5:]
            return self.player.take_item(item_name)
        elif command.startswith('use '):
            item_name = command[4:]
            return self.player.use_item(item_name)
        elif command.startswith('equip '):
            item_name = command[6:]
            return self.player.equip_item(item_name)
        elif command.startswith('unequip '):
            slot = command[8:]
            return self.player.unequip_item(slot)
        elif command in ['inventory', 'i']:
            if not self.player.inventory:
                return "Your inventory is empty."
            counts = {}
            for item in self.player.inventory:
                counts[item.name] = counts.get(item.name, 0) + 1
            lines = [f"- {name} x{qty}" if qty > 1 else f"- {name}" for name, qty in counts.items()]
            return "You are carrying:\n" + "\n".join(lines)
        elif command in ['stats', 's']:
            return (f"Health: {self.player.health}/{self.player.max_health}\n"
                    f"Attack: {self.player.attack}\n"
                    f"Defense: {self.player.defense}\n"
                    f"Speed: {self.player.speed}\n"
                    f"Crit Chance: {self.player.crit_chance*100:.1f}%\n"
                    f"Crit Multiplier: {self.player.crit_multiplier:.1f}x\n"
                    f"Experience: {self.player.experience}\n"
                    f"To next level: {self.player.xp_to_next_level - self.player.experience}")
        elif command.startswith('attack '):
            player_attack = command[7:]
            if self.player.current_room.enemy and self.player.current_room.enemy.name.lower() == player_attack:
                self.start_combat(self.player.current_room.enemy)
            else:
                return "There's no such enemy here."
        elif command.startswith('examine '):
            examine = command[8:]
            return self.player.examine(examine)
        elif command.startswith('read '):
            item_name = command[5:]
            item = next((i for i in self.player.inventory if i.name.lower() == item_name), None)
            if not item:
                return "You don't have that item."
            if hasattr(item, 'content') and item.content:
                return item.content
            return "There's nothing to read."
        elif command in ['help', 'h']:
            return ("Commands:\n"
                    "- look/l: Look around the room\n"
                    "- go [direction]: Move in a direction (north, south, east, west)\n"
                    "- take [item]: Pick up an item\n"
                    "- use [item]: Use a consumable item\n"
                    "- equip [item]: Equip an equippable item\n"
                    "- unequip [slot]: Unequip an item from a slot\n"
                    "- examine [item/enemy]: Examine an item or enemy\n"
                    "- read [item]: Read the content of an item (like a journal)\n"
                    "- inventory/i: Check your inventory\n"
                    "- stats/s: Check your stats\n"
                    "- attack [enemy]: Attack an enemy\n"
                    "- help/h: Show this help message")
        else:
            return "Unknown command."
        
    def print_combat_menu(self, player, enemy):
        print(f"[ {player.name} HP: {player.health}/{player.max_health} ] ----------vs---------- [ {enemy.name} HP: {enemy.health} ]")
        commands = [
            "[A] Attack",
            "[U] Use [item]",
            "[E] Equip [item]",
            "[Q] Unequip [slot]",
            "[R] Run",
            "[I] Inventory",
            "[S] Stats"
        ]
        width = max(max(len(l) for l in commands), 40) + 4
        border = "+" + "-" * (width - 2) + "+"
        output = [border]
        for line in commands:
            output.append("| " + line.ljust(width - 4) + " |")
        output.append(border)
        print("\n".join(output))
        
    def start_combat(self, enemy):
        print("\n" + "-" * 50)
        combat = Combat(self.player, enemy)
        initiative = combat.get_initiative()
        if initiative == 'player':
            print("You have the initiative! You attack first.")
        else:
            print(f"The {enemy.name} has the initiative! It attacks first.")
            damage, is_crit = combat.enemy_attack()
            crit_text = " \u001b[33mCritical hit!\u001b[0m" if is_crit else ""
            print(f"The {enemy.name} attacks you for {damage} damage!{crit_text} ({self.player.health}/{self.player.max_health} HP)")

        while not combat.is_over():
            # Player's turn
            self.print_combat_menu(self.player, enemy)
            player_action = input(">").strip().lower()
            if player_action in ('attack', 'a') or player_action.startswith('attack '):
                damage, is_crit = combat.player_attack()
                crit_text = " \u001b[33mCritical hit!\u001b[0m" if is_crit else ""
                print(f"You attack the {enemy.name} for {damage} damage!{crit_text}")
            elif player_action in ('use', 'u') or player_action.startswith('use ') or player_action.startswith('u '):
                if player_action in ('use', 'u'):
                    player_action = 'use ' + input("Use which item? ").strip().lower()
                elif player_action.startswith('u '):
                    player_action = 'use ' + player_action[2:]
                print(self.player.use_item(player_action[4:]))
            elif player_action in ('equip', 'e') or player_action.startswith('equip ') or player_action.startswith('e '):
                if player_action in ('equip', 'e'):
                    player_action = 'equip ' + input("Equip which item? ").strip().lower()
                elif player_action.startswith('e '):
                    player_action = 'equip ' + player_action[2:]
                print(self.player.equip_item(player_action[6:]))
                continue
            elif player_action in ('unequip', 'q') or player_action.startswith('unequip ') or player_action.startswith('q '):
                if player_action in ('unequip', 'q'):
                    player_action = 'unequip ' + input("Unequip which slot? ").strip().lower()
                elif player_action.startswith('q '):
                    player_action = 'unequip ' + player_action[2:]
                print(self.player.unequip_item(player_action[8:]))
                continue
            elif player_action in ('run', 'r') or player_action.startswith('run'):
                if combat.try_escape():
                    print("You successfully escaped!")
                    return
                print("You failed to escape!")
            elif player_action in ('stats', 's'):
                print(self.process_command('stats'))
                continue
            elif player_action in ('inventory', 'i'):
                print(self.process_command('inventory'))
                continue
            else:
                print("Invalid action, try again.")
                continue

            if combat.is_over():
                break

            # Enemy's turn
            damage, is_crit = combat.enemy_attack()
            crit_text = " \u001b[33mCritical hit!\u001b[0m" if is_crit else ""
            print(f"The {enemy.name} attacks you for {damage} damage!{crit_text}")
            self.player.tick_buffs()

        if self.player.is_alive:
            print(f"You defeated the {enemy.name}!")
            self.enemies_defeated += 1
            print(f"You gained {enemy.xp_reward} XP!")
            self.player.gain_experience(enemy.xp_reward)
            if enemy.loot:
                print("You found the following loot:")
                for item_id in enemy.loot:
                    item = self.item_catalogue.get(item_id)
                    if item:
                        self.player.inventory.append(item)
                        print(f"- {item.name}")
            weapon = self.player.equipped.get('weapon')
            if weapon and hasattr(weapon, 'register_kill'):
                weapon.register_kill(self.player)
            if self.player.current_room.is_final:
                self.running = False
                self.outcome = 'win'
        else:
            print("You have been defeated...")
            self.running = False
            self.outcome = 'death'
        print("-" * 50 + "\n")
        