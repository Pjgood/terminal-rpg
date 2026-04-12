import nt

from Models.item import Consumable


class Player:
    def __init__(self, name, health, attack, defense, speed, 
                 crit_chance, crit_multiplier, level=1, experience=0):
        self.name = name
        self.max_health = health
        self.health = health
        self.defense = defense
        self.speed = speed
        self.attack = attack
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
        self.level = level
        self.experience = experience
        self.xp_to_next_level = 100
        self.inventory = []
        self.active_buffs = []
        self.current_room = None

        self.equipped = {
            'weapon': None,
            'head': None,
            'body': None,
            'legs': None,
            'accessory': None
        }

    def move(self, direction, rooms):
        if direction in self.current_room.connections:
            new_room_id = self.current_room.connections[direction]
            self.current_room = rooms[new_room_id]
            return True
        return False

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def tick_buffs(self):
        for buff in self.active_buffs[:]:
            buff['duration'] -= 1
            if buff['duration'] <= 0:
                self.attack -= buff['attack']
                self.defense -= buff['defense']
                self.speed -= buff['speed']
                self.crit_chance -= buff['crit_chance']
                self.crit_multiplier -= buff['crit_multiplier']
                self.active_buffs.remove(buff)

    def take_item(self, item_name):
        item = next((i for i in self.current_room.items if i.name.lower() == item_name.lower()), None)
        if not item:
            return "There's no such item here."
        self.inventory.append(item)
        self.current_room.items.remove(item)
        return f"You picked up the {item.name}."

    def use_item(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            return "You don't have that item."
        if isinstance(item, Consumable):
            result = item.use(self)
            self.inventory.remove(item)
            return result
        else:
            return "You can't use that item."
        
    def equip_item(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            return "You don't have that item."
        if hasattr(item, 'equip'):
            result = item.equip(self)
            self.inventory.remove(item)
            return result
        else:
            return "You can't equip that item."
        
    def unequip_item(self, slot_or_name):
        current_item = self.equipped.get(slot_or_name)
        if not current_item:
            for slot, item in self.equipped.items():
                if item and item.name.lower() == slot_or_name.lower():
                    current_item = item
                    slot_or_name = slot
                    break
        if current_item:
            result = current_item.unequip(self)
            self.inventory.append(current_item)
            return result
        else:
            return f"You don't have anything equipped in the {slot_or_name} slot."
        
    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.xp_to_next_level:
            self.level_up()
        
    def level_up(self):
        self.experience -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.25)
        self.level += 1
        # Old values
        old_health = self.max_health
        old_attack = self.attack
        old_defense = self.defense
        old_speed = self.speed
        old_crit_chance = self.crit_chance
        old_crit_multiplier = self.crit_multiplier

        # Apply increases
        self.max_health += 10
        self.health = self.max_health
        self.attack += 3
        self.defense += 1
        self.speed += 1
        self.crit_chance += 0.01
        self.crit_multiplier += 0.1

        #Display
        lines = [
              f"Level up! You are now level {self.level}!",
              f"Your stats have increased!",
              f"Health: {old_health} -> {self.max_health}",
              f"Attack: {old_attack} -> {self.attack}",
              f"Defense: {old_defense} -> {self.defense}",
              f"Speed: {old_speed} -> {self.speed}",
              f"Crit Chance: {old_crit_chance*100:.1f}% -> {self.crit_chance*100:.1f}%",
              f"Crit Multiplier: {old_crit_multiplier} -> {self.crit_multiplier}"
        ]

        width = max(max(len(l) for l in lines), 40) + 4
        border = "+" + "-" * (width - 2) + "+"
        output = [border]
        for line in lines:
            output.append("| " + line.ljust(width - 4) + " |")
        output.append(border)
        print("\n".join(output))


    def examine(self, target):
        item = next((i for i in self.inventory if i.name.lower() == target.lower()), None)
        if item:
            return f"{item.name}: {item.description}"
        for item in self.equipped.values():
            if item and item.name.lower() == target.lower():
                return f"{item.name}: {item.description}"
        if self.current_room.enemy and self.current_room.enemy.name.lower() == target.lower():
            return f"{self.current_room.enemy.name}: {self.current_room.enemy.description}"
        item = next((i for i in self.current_room.items if i.name.lower() == target.lower()), None)
        if item:
            return f"{item.name}: {item.description}"
        return "You don't see that here."
    

    @property        
    def is_alive(self):
        return self.health > 0