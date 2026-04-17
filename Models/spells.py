import time

class Spell:
    def __init__(self, name, description, mana_cost, damage,
                 base_damage=None, scaling_factor=0.0,
                 cast_thresholds=None, tiers=None, unlock_triggers=None,
                 art=None, status_effect=None, animation=None, animation_options=None):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.damage = damage
        self.base_damage = base_damage if base_damage is not None else damage
        self.scaling_factor = scaling_factor
        self.status_effect = status_effect
        self.animation = animation  # 'lines', 'frames', or None
        self.cast_count = 0
        self.cast_thresholds = cast_thresholds if cast_thresholds else []
        self.tiers = tiers if tiers else []
        self.unlock_triggers = unlock_triggers if unlock_triggers else []
        self.art = art  # ASCII string, optional
        self.impact_frame = None  # set via world_loader
        self.animation_options = animation_options if animation_options else {}
    def cast(self, player, enemy):
        if player.mana < self.mana_cost:
            return f"Not enough mana! ({player.mana}/{self.mana_cost} MP)"
        player.mana -= self.mana_cost
        import random
        damage = int(self.base_damage + player.attack * self.scaling_factor)
        enemy.take_damage(damage)
        self.cast_count += 1
        self._check_tier_up()
        result = f"You cast {self.name} for {damage} damage!"
        if self.status_effect:
            effect = self.status_effect
            if random.random() < effect.get('chance', 0):
                debuff = {'type': effect['type'], 'duration': effect.get('duration', 2)}
                if effect['type'] == 'shock':
                    debuff['multiplier'] = effect.get('multiplier', 1.5)
                elif effect['type'] == 'frost':
                    debuff['skip_chance'] = effect.get('skip_chance', 0.5)
                elif effect['type'] == 'burn':
                    debuff['damage'] = effect.get('damage', 5)
                enemy.active_debuffs.append(debuff)
                status_past_tense = {'frost': 'frozen', 'shock': 'shocked', 'burn': 'burned'}
                status_word = status_past_tense.get(effect['type'], effect['type'] + 'ed')
                result += f" The {enemy.name} is {status_word}!"
        if self.art:
            if self.animation == 'frames' and isinstance(self.art, list):
                opts = self.animation_options or {}
                frame_delay = opts.get('frame_delay', 0.5)
                second_last_delay = opts.get('second_last_delay', frame_delay)
                last_frame_delay = opts.get('last_frame_delay', frame_delay)
                invert_last = opts.get('invert_last_frame', False)
                for i, frame in enumerate(self.art):
                    is_last = i == len(self.art) - 1
                    second_last = i == len(self.art) - 2
                    if is_last:
                        if invert_last:
                            print(f"\033[7m{frame}\033[0m")
                        else:
                            print(frame)
                        time.sleep(last_frame_delay)
                    elif second_last:
                        print(frame)
                        time.sleep(second_last_delay)
                        line_count = frame.count('\n') + 1
                        print(f"\033[{line_count}A", end="")
                    else:
                        print(frame)
                        time.sleep(frame_delay)
                        line_count = frame.count('\n') + 1
                        print(f"\033[{line_count}A", end="")
            else:
                lines = self.art.split('\n')
                for i in range(0, len(lines), 2):
                    print(lines[i])
                    if i + 1 < len(lines):
                        print(lines[i + 1])
                    time.sleep(0.5)
                if self.impact_frame:
                    line_count = len(lines)
                    print(f"\033[{line_count}A", end="")
        if self.impact_frame:
            print(f"\033[7m{self.impact_frame}\033[0m")
            time.sleep(0.6)
        return result

    def _check_tier_up(self):
        if self.cast_thresholds and self.cast_count == self.cast_thresholds[0]:
            self.cast_thresholds.pop(0)
            tier = self.tiers.pop(0)
            self.name = tier['name']
            self.description = tier['description']
            self.damage = tier['damage']
            self.mana_cost = tier.get('mana_cost', self.mana_cost)
            print(f"Your spell has grown stronger: {self.name}!")