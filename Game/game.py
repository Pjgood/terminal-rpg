import json
import os
import sys
from random import random

from Models import grimoire, player
from Models import enemy
from Models.player import Player
from Models.enemy import Enemy
from Systems.world_loader import WorldLoader
from Systems.combat import Combat
from Systems.map_renderer import render_map
from Systems.special_abilities import use_beats, use_bepop, use_defuse


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
        self.player = Player("Hero", health=100, mana=60, mana_regen=5, attack=10, 
                             defense=5, speed=5, crit_chance=0.1, crit_multiplier=2)
        self.rooms = {}
        self.running = True
        self.outcome = None
        self.enemies_defeated = 0

    def load_world(self):
        loader = WorldLoader(_resource_path("Assets/Data/rooms.json"), _resource_path("Assets/Data/items.json"), _resource_path("Assets/Data/spells.json"))
        self.rooms, self.item_catalogue = loader.load()
        for room in self.rooms.values():
            room.item_catalogue = self.item_catalogue
        self.player.current_room = self.rooms['subway_platform']
        self.player.visited_rooms.add('subway_platform')

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
                    self.start_combat(self.player.current_room.enemies)
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
            return (f"Level: {self.player.level}\n"
                    f"Health: {self.player.health}/{self.player.max_health}\n"
                    f"Attack: {self.player.attack}\n"
                    f"Defense: {self.player.defense}\n"
                    f"Speed: {self.player.speed}\n"
                    f"Crit Chance: {self.player.crit_chance*100:.1f}%\n"
                    f"Crit Multiplier: {self.player.crit_multiplier:.1f}x\n"
                    f"Mana: {self.player.mana}/{self.player.max_mana}\n"
                    f"Mana Regen: {self.player.mana_regen}\n"
                    f"Experience: {self.player.experience}\n"
                    f"To next level: {self.player.xp_to_next_level - self.player.experience}")
        elif command.startswith('attack '):
            player_attack = command[7:]
            if self.player.current_room.enemy and self.player.current_room.enemy.name.lower() == player_attack:
                self.start_combat(self.player.current_room.enemies)
            else:
                return "There's no such enemy here."
        elif command.startswith('examine '):
            examine = command[8:]
            message, damage = self.player.examine(examine)
            if damage > 0:
                self.player.health -= damage
                message += f"\n(-{damage} HP)"
            return message
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
        elif command == 'map':
            current_room_id = next(k for k, v in self.rooms.items() if v is self.player.current_room)
            floor = getattr(self.player.current_room, 'floor', 1)
            render_map(self.rooms, self.player.visited_rooms, current_room_id, floor=floor)
        elif command.startswith('save'):
            parts = command.split()
            filename = parts[1] if len(parts) > 1 else 'save.json'
            try:
                self.save(filename)
                return f"Game saved to {filename}."
            except Exception as e:
                return f"Failed to save game: {e}"      
        elif command.startswith('drink '):
            target = command[6:]
            if target == 'water' and self.player.current_room.name == 'Sewer':
                print("You lean down and drink deeply of the foul water.")
                print("You were warned.")
                self.running = False
                self.outcome = 'death'
        else:
            return "Unknown command."
        
    def print_combat_menu(self, player, enemies):
        alive = [e for e in enemies if e.is_alive]
        enemy_str = " | ".join(f"{e.name} HP: {e.health}" for e in alive)
        print(f"[ {player.name} HP: {player.health}/{player.max_health} MP: {player.mana}/{player.max_mana} ] ----------vs---------- [ {enemy_str} ]")
        commands = [
            "[A] Attack"]
        if any(hasattr(i, 'get_spell') for i in player.inventory):
             commands.append("[C] Cast Spell")
        commands += [
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
        
    def start_combat(self, enemies):
        print("\n" + "-" * 50)
        combat = Combat(self.player, enemies)
        initiative = combat.get_initiative()
        if initiative == 'player':
            print("You have the initiative! You attack first.")
        else:
            fastest = max(enemies, key=lambda e: e.speed)
            print(f"The {fastest.name} has the initiative! It attacks first.")
            for e, dmg, crit in combat.enemy_attack():
                crit_text = " \u001b[33mCritical hit!\u001b[0m" if crit else ""
                print(f"The {e.name} attacks you for {dmg} damage!{crit_text}")
            print(f"({self.player.health}/{self.player.max_health} HP)")

        while not combat.is_over():
            # Player's turn
            self.print_combat_menu(self.player, enemies)  # Show all enemies
            player_action = input(">").strip().lower()
            if player_action in ('attack', 'a') or player_action.startswith('attack ') or player_action.startswith('a '):
                target_name = player_action[7:] if player_action.startswith('attack ') else (player_action[2:] if player_action.startswith('a ') else None)
                target = next((e for e in enemies if e.name.lower() == target_name), None) if target_name else next((e for e in enemies if e.is_alive), None)
                damage, is_crit = combat.player_attack(target)
                crit_text = " \u001b[33mCritical hit!\u001b[0m" if is_crit else ""
                print(f"You attack the {target.name} for {damage} damage!{crit_text}")
            elif player_action in ('cast', 'c') or player_action.startswith('cast '):
                grimoire = next((i for i in self.player.inventory if hasattr(i, 'get_spell')), None)
                if not grimoire:
                    print("You don't have a grimoire.")
                    continue
                if player_action in ('cast', 'c'):
                    print(grimoire.list_spells())
                    spell_name = input("Cast which spell? ").strip().lower()
                    target_name = player_action[player_action.find(spell_name) + len(spell_name):].strip() if spell_name in player_action else None
                elif player_action.startswith('c '):
                    spell_name = player_action[2:].strip().lower()
                    target_name = None
                else:
                    spell_name = player_action[5:]
                spell = grimoire.get_spell(spell_name)
                if not spell:
                    print("You don't know that spell.")
                    continue
                target = next((e for e in enemies if e.is_alive), None)
                print(spell.cast(self.player, target))
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
            elif player_action in ('special', 'p') or player_action.startswith('special '):
                if self.player.special_ability == 'Bepop':
                    print(use_bepop(self.player, enemies))
                if self.player.special_ability == 'Beats':
                    print(use_beats(self.player, enemies))
                if self.player.special_ability == 'Defuse':
                    print(use_defuse(self.player, enemies))
            else:
                print("Invalid action, try again.")
                continue

            if combat.is_over():
                break

            # Enemy's turn
            for e in enemies:
                if e.is_alive:
                    for msg in e.tick_debuffs():
                        print(msg)
            if combat.is_over():
                break
            for e in enemies:
                    if e.is_alive and e.is_frozen():
                        print(f"The {e.name} is frozen and cannot move!")
            for e, dmg, crit in combat.enemy_attack():
                    crit_text = " \u001b[33mCritical hit!\u001b[0m" if crit else ""
                    print(f"The {e.name} attacks you for {dmg} damage!{crit_text}")
            self.player.tick_buffs()

        if self.player.is_alive:
            total_xp = 0
            for e in enemies:
                print(f"You defeated the {e.name}!")
                self.enemies_defeated += 1
                total_xp += e.xp_reward
                if e.loot:
                    print("You found the following loot:")
                    for item_id in e.loot:
                        item = self.item_catalogue.get(item_id)
                        if item:
                            self.player.inventory.append(item)
                            print(f"- {item.name}")
            print(f"You gained {total_xp} XP!")
            self.player.gain_experience(total_xp)
            self.player.regen_mana()
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
    
    def save(self, filename='savegame.json'):
        # Find grimoire in inventory if present
        grimoire = next((i for i in self.player.inventory if hasattr(i, 'unlocked_spells')), None)
        unlocked_spells = [s.name for s in grimoire.unlocked_spells] if grimoire else []

        # Find item IDs by reverse-looking up the item catalogue
        inv_ids = [k for item in self.player.inventory for k, v in self.item_catalogue.items() if v is item]
        equipped_ids = {slot: next((k for k, v in self.item_catalogue.items() if v is item), None)
                    for slot, item in self.player.equipped.items() if item}

        # Which rooms have all enemies defeated
        cleared_rooms = [room_id for room_id, room in self.rooms.items()
                     if room.enemies and all(not e.is_alive for e in room.enemies)]

        data = {
            'player_name': self.player.name,
            'health': self.player.health,
            'mana': self.player.mana,
            'level': self.player.level,
            'experience': self.player.experience,
            'attack': self.player.attack,
            'defense': self.player.defense,
            'speed': self.player.speed,
            'max_health': self.player.max_health,
            'max_mana': self.player.max_mana,
            'mana_regen': self.player.mana_regen,
            'crit_chance': self.player.crit_chance,
            'crit_multiplier': self.player.crit_multiplier,
            'xp_to_next_level': self.player.xp_to_next_level,
            'current_room': next(k for k, v in self.rooms.items() if v is self.player.current_room),
            'inventory': inv_ids,
            'equipped': equipped_ids,
            'unlocked_spells': unlocked_spells,
            'examined_targets': self.player.examined_targets,
            'cleared_rooms': cleared_rooms,
            'enemies_defeated': self.enemies_defeated,
            'visited_rooms': list(self.player.visited_rooms)
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print("Game saved.")

    def load(self, filename='savegame.json'):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.player.name = data['player_name']
        self.player.health = data['health']
        self.player.mana = data['mana']
        self.player.level = data['level']
        self.player.experience = data['experience']
        self.player.attack = data['attack']
        self.player.defense = data['defense']
        self.player.speed = data['speed']
        self.player.max_health = data['max_health']
        self.player.max_mana = data['max_mana']
        self.player.mana_regen = data['mana_regen']
        self.player.crit_chance = data['crit_chance']
        self.player.crit_multiplier = data['crit_multiplier']
        self.player.xp_to_next_level = data['xp_to_next_level']
        self.player.current_room = self.rooms[data['current_room']]
        self.player.inventory = [self.item_catalogue[i] for i in data['inventory'] if i in self.item_catalogue]
        grimoire = next((i for i in self.player.inventory if hasattr(i, 'unlocked_spells')), None)
        if grimoire:
            grimoire.unlocked_spells = [s for s in grimoire.spells if s.name in data.get('unlocked_spells', [])]
        self.player.equipped = {slot: self.item_catalogue[i] for slot, i in data['equipped'].items() if i in self.item_catalogue}
        self.player.examined_targets = data.get('examined_targets', [])
        self.enemies_defeated = data.get('enemies_defeated', 0)
        cleared = data.get('cleared_rooms', [])
        for room_id in cleared:
            if room_id in self.rooms:
                room = self.rooms[room_id]
                for e in room.enemies:
                    e.health = 0
        self.player.visited_rooms = set(data.get('visited_rooms', []))
        print("Game loaded.")
