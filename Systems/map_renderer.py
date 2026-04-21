def render_map(rooms, visited_rooms, current_room_id, floor=1):
    """
    Print an ASCII grid map for the given floor.
    Each room in rooms must have a 'pos': [x, y] attribute.
    """
    # Filter rooms for the current floor and collect positions
    floor_rooms = {rid: r for rid, r in rooms.items() if hasattr(r, 'pos') and r.pos is not None and int(getattr(r, 'floor', 1)) == int(floor)}
    if not floor_rooms:
        print(f"No map data for floor {floor}.")
        print("Debug: All rooms and their floor/pos:")
        for rid, r in rooms.items():
            print(f"  {rid}: floor={getattr(r, 'floor', None)}, pos={getattr(r, 'pos', None)}")
        return

    # Find grid bounds
    xs = [r.pos[0] for r in floor_rooms.values()]
    ys = [r.pos[1] for r in floor_rooms.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Build grid (flip vertically: highest y at top, lowest y at bottom)
    grid = []
    for y in range(max_y, min_y - 1, -1):
        row = []
        for x in range(min_x, max_x + 1):
            rid = next((rid for rid, r in floor_rooms.items() if r.pos == [x, y]), None)
            if rid:
                if rid == current_room_id:
                    cell = "@"
                elif rid in visited_rooms:
                    cell = "*"
                else:
                    cell = " "  # Only show visited/current rooms
            else:
                cell = " "
            row.append(cell)
        grid.append(row)

    print(f"Map - Floor {floor}")
    for row in grid:
        print(" ".join(row))
    print("Legend: @ = you, * = visited, blank = unexplored/no room")