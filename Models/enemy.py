class Enemy:
    def __init__(self, name, description, health, attack, defense, speed, 
                 crit_chance, crit_multiplier, xp_reward, escape_difficulty=0.3,
                 loot=None, freeze_resistance=0.0):
        self.name = name
        self.description = description
        self.health = health
        self.defense = defense
        self.speed = speed
        self.attack = attack
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
        self.xp_reward = xp_reward
        self.escape_difficulty = escape_difficulty
        self.loot = loot if loot is not None else []
        self.freeze_resistance = freeze_resistance
        self.active_debuffs = []


    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def tick_debuffs(self):
        """Process all active debuffs. Returns a list of messages to print."""
        messages = []
        for debuff in self.active_debuffs[:]:
            debuff['duration'] -= 1
            if debuff['type'] == 'burn':
                self.take_damage(debuff['damage'])
                messages.append(f"The {self.name} burns for {debuff['damage']} damage!")
            if debuff['duration'] <= 0:
                self.active_debuffs.remove(debuff)
                messages.append(f"The {self.name} is no longer {debuff['type']}ed.")
        return messages

    def is_frozen(self):
        """Returns True if a frost debuff procs a turn skip."""
        import random
        for debuff in self.active_debuffs:
            if debuff['type'] == 'frost':
                effective_chance = debuff['skip_chance'] * (1.0 - self.freeze_resistance)
                if random.random() < effective_chance:
                    return True
        return False

    def shock_multiplier(self):
        """Returns damage multiplier from shock, or 1.0 if none."""
        for debuff in self.active_debuffs:
            if debuff['type'] == 'shock':
                return debuff['multiplier']
        return 1.0

    @property        
    def is_alive(self):
        return self.health > 0