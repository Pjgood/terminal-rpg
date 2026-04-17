import random

class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def player_attack(self):
        base_attack = self.player.attack
        damage = random.randint(int(base_attack *0.8), int(base_attack *1.2))
        is_crit = random.random() < self.player.crit_chance
        if is_crit:
            damage *= self.player.crit_multiplier
        damage -= self.enemy.defense
        if damage < 0:
            damage = 0
        damage = int(damage * self.enemy.shock_multiplier())
        self.enemy.take_damage(damage)
        return damage, is_crit

    def enemy_attack(self):
        base_attack = self.enemy.attack
        damage = random.randint(int(base_attack *0.8), int(base_attack *1.2))
        is_crit = random.random() < self.enemy.crit_chance
        if is_crit:
            damage *= self.enemy.crit_multiplier
        damage -= self.player.defense
        if damage < 0:
            damage = 0
        damage = int(damage)
        self.player.take_damage(damage)
        return damage, is_crit

    def is_over(self):
        if not self.player.is_alive:
            return True
        if not self.enemy.is_alive:
            return True
        return False
    
    def get_initiative(self):
        player_initiative = self.player.speed + random.randint(1, 20)
        enemy_initiative = self.enemy.speed + random.randint(1, 20)
        if player_initiative > enemy_initiative:
            return 'player'
        elif enemy_initiative > player_initiative:
            return 'enemy'
        elif player_initiative == enemy_initiative:
            return 'player' if random.random() < 0.5 else 'enemy'
        
    def try_escape(self):
        return random.random() > self.enemy.escape_difficulty
