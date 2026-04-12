class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Consumable(Item):
    def __init__(self, name, description, heal_amount, duration=0, attack_bonus=0, defense_bonus=0,
                  speed_bonus=0, crit_chance_bonus=0, crit_multiplier_bonus=0):
        super().__init__(name, description)
        self.heal_amount = heal_amount
        self.attack_bonus = attack_bonus
        self.duration = duration
        self.defense_bonus = defense_bonus
        self.speed_bonus = speed_bonus
        self.crit_chance_bonus = crit_chance_bonus
        self.crit_multiplier_bonus = crit_multiplier_bonus

    def use(self, player):
        player.health = min(player.max_health, player.health + self.heal_amount)  # Cap health at max_health
        if self.duration > 0:
            buff = {
                'attack': self.attack_bonus,
                'defense': self.defense_bonus,
                'speed': self.speed_bonus,
                'crit_chance': self.crit_chance_bonus,
                'crit_multiplier': self.crit_multiplier_bonus,
                'duration': self.duration
                }
            player.active_buffs.append(buff)
            player.attack += self.attack_bonus
            player.defense += self.defense_bonus
            player.speed += self.speed_bonus
            player.crit_chance += self.crit_chance_bonus
            player.crit_multiplier += self.crit_multiplier_bonus
        messages = [f"{player.name} used {self.name}."]
        if self.heal_amount > 0:
            messages.append(f"Healed for {self.heal_amount} HP. ({player.health}/{player.max_health})")
        if self.duration > 0:
            if self.attack_bonus:
                messages.append(f"Attack +{self.attack_bonus} for {self.duration} turns.")
            if self.defense_bonus:
                messages.append(f"Defense +{self.defense_bonus} for {self.duration} turns.")
            if self.speed_bonus:
                messages.append(f"Speed +{self.speed_bonus} for {self.duration} turns.")
            if self.crit_chance_bonus:
                messages.append(f"Crit Chance +{self.crit_chance_bonus*100:.1f}% for {self.duration} turns.")
            if self.crit_multiplier_bonus:
                messages.append(f"Crit Multiplier +{self.crit_multiplier_bonus:.1f}x for {self.duration} turns.")
        return "\n".join(messages)
        

class Equippable(Item):
    def __init__(self, name, description, slot, attack_bonus=0, defense_bonus=0, speed_bonus=0,
                 crit_chance_bonus=0, crit_multiplier_bonus=0, health_penalty_percent=0.0,
                 kill_thresholds=None, tiers=None):
        super().__init__(name, description)
        self.slot = slot
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.speed_bonus = speed_bonus
        self.crit_chance_bonus = crit_chance_bonus
        self.crit_multiplier_bonus = crit_multiplier_bonus
        self.health_penalty_percent = health_penalty_percent
        self.kill_count = 0
        self.kill_thresholds = kill_thresholds if kill_thresholds is not None else []
        self.tiers = tiers if tiers is not None else []

    def equip(self, player):
        current_item = player.equipped.get(self.slot)
        if current_item:
            player.attack -= current_item.attack_bonus
            player.defense -= current_item.defense_bonus
            player.speed -= current_item.speed_bonus
            player.crit_chance -= current_item.crit_chance_bonus
            player.crit_multiplier -= current_item.crit_multiplier_bonus
            if current_item.health_penalty_percent > 0:
                penalty = int(player.max_health / (1 - current_item.health_penalty_percent)) - player.max_health
                player.max_health += penalty
        player.equipped[self.slot] = self
        player.attack += self.attack_bonus
        player.defense += self.defense_bonus
        player.speed += self.speed_bonus
        player.crit_chance += self.crit_chance_bonus
        player.crit_multiplier += self.crit_multiplier_bonus
        if self.health_penalty_percent > 0:
            penalty = int(player.max_health * self.health_penalty_percent)
            player.max_health -= penalty
            player.health = min(player.health, player.max_health)
        return f"{player.name} equipped {self.name} in the {self.slot} slot."
    
    def unequip(self, player):
        current_item = player.equipped.get(self.slot)
        if current_item is self:
            player.attack -= current_item.attack_bonus
            player.defense -= current_item.defense_bonus
            player.speed -= current_item.speed_bonus
            player.crit_chance -= current_item.crit_chance_bonus
            player.crit_multiplier -= current_item.crit_multiplier_bonus
            if current_item.health_penalty_percent > 0:
                penalty = int(player.max_health / (1 - self.health_penalty_percent) - player.max_health)
                player.max_health += penalty
            player.equipped[self.slot] = None
            return f"{player.name} unequipped {current_item.name} from the {self.slot} slot."
        return f"No item to unequip in the {self.slot} slot."
    
    def register_kill(self, player):
        if not self.kill_thresholds:
            return
        self.kill_count += 1
        if self.kill_count in self.kill_thresholds and self.tiers:
            tier = self.tiers.pop(0)
            self.name = tier['name']
            self.description = tier['description']
            player.attack += tier['attack_increase']
            self.attack_bonus += tier.get('attack_increase')
            print(f"Your weapon has grown stronger: {self.name}! \n{self.description}")


class Key(Item):
    def __init__(self, name, description, key_id, content=None):
        super().__init__(name, description)
        self.key_id = key_id
        self.content = content