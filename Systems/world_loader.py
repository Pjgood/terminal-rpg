import json
from Models.enemy import Enemy
from Models.room import Room
from Models.item import Consumable, Equippable, Key

class WorldLoader:
    def __init__(self, rooms_path, items_path):
        self.rooms_path = rooms_path
        self.items_path = items_path

    def load(self):
        # returns a dict of {room_id: Room object}
        with open(self.rooms_path, 'r') as f:
            rooms_data = json.load(f)
        with open(self.items_path, 'r') as f:
            items_data = json.load(f)
        item_catalogue = {item_id: self._build_item(item_data) for item_id, item_data in items_data.items()}
        rooms = {room_id: self._build_room(room_id, room_data, item_catalogue) for room_id, room_data in rooms_data.items()}
        return rooms, item_catalogue

    def _build_item(self, item_data):
        item_type = item_data['type']
        if item_type == 'consumable':
            return Consumable(
                name=item_data['name'],
                description=item_data['description'],
                heal_amount=item_data['heal_amount'],
                duration=item_data.get('duration', 0),
                attack_bonus=item_data.get('attack_bonus', 0),
                defense_bonus=item_data.get('defense_bonus', 0),
                speed_bonus=item_data.get('speed_bonus', 0),
                crit_chance_bonus=item_data.get('crit_chance_bonus', 0),
                crit_multiplier_bonus=item_data.get('crit_multiplier_bonus', 0)
            )
        elif item_type == 'equippable':
            return Equippable(
                name=item_data['name'],
                description=item_data['description'],
                slot=item_data['slot'],
                attack_bonus=item_data.get('attack_bonus', 0),
                defense_bonus=item_data.get('defense_bonus', 0),
                speed_bonus=item_data.get('speed_bonus', 0),
                crit_chance_bonus=item_data.get('crit_chance_bonus', 0),
                crit_multiplier_bonus=item_data.get('crit_multiplier_bonus', 0),
                health_penalty_percent=item_data.get('health_penalty_percent', 0.0),
                kill_thresholds=item_data.get('kill_threshold', []),
                tiers=item_data.get('tiers', [])
            )
        elif item_type == 'key':
            return Key(
                name=item_data['name'],
                description=item_data['description'],
                key_id=item_data['key_id'],
                content=item_data.get('content', None)
            )
        else:
            raise ValueError(f"Unknown item type: {item_type}")

    def _build_room(self, room_id, room_data, item_catalogue):
        items = [item_catalogue[item_id] for item_id in room_data.get('items', []) if item_id in item_catalogue]
        enemy_data = room_data.get('enemy')
        enemy = self._build_enemy(enemy_data) if enemy_data else None
        return Room(
            name=room_data['name'],
            description=room_data['description'],
            connections=room_data['connections'],
            image_paths=room_data.get('image_paths', {}),
            items=items,
            enemy=enemy,
            locked=room_data.get('locked', False),
            required_key=room_data.get('required_key', None),
            is_final=room_data.get('is_final', False),
            blocks_exits=room_data.get('blocks_exits', [])
        )
    
    def _build_enemy(self, enemy_data):
        return Enemy(
            name=enemy_data['name'],
            description=enemy_data['description'],
            health=enemy_data['health'],
            attack=enemy_data['attack'],
            defense=enemy_data['defense'],
            speed=enemy_data['speed'],
            crit_chance=enemy_data.get('crit_chance', 0.1),
            crit_multiplier=enemy_data.get('crit_multiplier', 1.5),
            xp_reward=enemy_data.get('xp_reward', 10),
            escape_difficulty=enemy_data.get('escape_difficulty', 0.3),
            loot=enemy_data.get('loot', [])
        )