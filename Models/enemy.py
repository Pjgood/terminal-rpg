class Enemy:
    def __init__(self, name, description, health, attack, defense, speed, 
                 crit_chance, crit_multiplier, xp_reward, escape_difficulty=0.3,
                 loot=None):
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


    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            
    @property        
    def is_alive(self):
        return self.health > 0