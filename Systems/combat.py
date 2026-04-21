import random

class Combat:
    def __init__(self, player, enemies = None):
        self.player = player
        self.enemies = enemies if enemies is not None else []

    def player_attack(self, target):
        base_attack = self.player.attack
        damage = random.randint(int(base_attack *0.8), int(base_attack *1.2))
        is_crit = random.random() < self.player.crit_chance
        if is_crit:
            damage *= self.player.crit_multiplier
        damage -= target.defense
        if damage < 0:
            damage = 0
        damage = int(damage * target.shock_multiplier())
        target.take_damage(damage)
        return damage, is_crit

    def enemy_attack(self):
        results = []
        for enemy in self.enemies:
            if enemy.is_alive:
                if enemy.is_frozen():
                    continue
                base_attack = enemy.attack
                damage = random.randint(int(base_attack * 0.8), int(base_attack * 1.2))
                is_crit = random.random() < enemy.crit_chance
                if is_crit:
                    damage *= enemy.crit_multiplier
                damage -= self.player.defense
                if damage < 0:
                    damage = 0
                self.player.take_damage(int(damage))
                results.append((enemy, int(damage), is_crit))
        return results

    def is_over(self):
        if not self.player.is_alive:
            return True
        if not any(enemy.is_alive for enemy in self.enemies):
            return True
        return False
    
    def get_initiative(self):
        player_initiative = self.player.speed + random.randint(1, 20)
        fastest = max(self.enemies, key=lambda e: e.speed)
        enemy_initiative = fastest.speed + random.randint(1, 20)
        if player_initiative > enemy_initiative:
            return 'player'
        elif enemy_initiative > player_initiative:
            return 'enemy'
        elif player_initiative == enemy_initiative:
            return 'player' if random.random() < 0.5 else 'enemy'
        
    def try_escape(self):
        hardest = max(self.enemies, key=lambda e: e.escape_difficulty)
        return random.random() > hardest.escape_difficulty
