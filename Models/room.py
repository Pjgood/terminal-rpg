class Room:
    def __init__(self, name, description, connections, image_paths, items=None,
                 locked=False, required_key=None, is_final=False, blocks_exits=None, examinables=None,
                 enemies=None, floor=None, pos=None):
        self.name = name
        self.description = description
        self.connections = connections  # {'north': room_id}
        self.image_paths = image_paths  # {'north': 'path.png'}
        self.items = items if items is not None else []
        self.examinables = examinables if examinables is not None else {}
        self.enemies = enemies if enemies is not None else []
        self.locked = locked
        self.required_key = required_key
        self.is_final = is_final
        self.blocks_exits = blocks_exits if blocks_exits is not None else []
        self.floor = floor if floor is not None else 1
        self.pos = pos


    def describe(self):
        lines = [self.name, ""]
        lines.extend(self.description.split('\n'))
        if self.items:
            lines.append(f"Items here: {', '.join(item.name for item in self.items)}")
        if self.enemies:
            alive_enemies = [enemy for enemy in self.enemies if enemy.is_alive]
            if alive_enemies:
                lines.append(f"Enemies: {', '.join(enemy.name for enemy in alive_enemies)}")
        lines.append("")
        lines.append(f"Exits: {', '.join(self.connections.keys())}")
        width = max(max(len(l) for l in lines), 40) + 4
        border = "+" + "-" * (width - 2) + "+"
        output = [border]
        for line in lines:
            output.append("| " + line.ljust(width - 4) + " |")
        output.append(border)
        return "\n".join(output)
    
    @property
    def enemy(self):
        return next((enemy for enemy in self.enemies if enemy.is_alive), None)