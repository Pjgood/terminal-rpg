import random
import time
import msvcrt


def use_bepop(player, enemies):
    target = next((e for e in enemies if e.is_alive), None)
    if not target:
        return "There is nothing to quickdraw against."

    print("\nBepop Quickdraw!")
    print(f"The {target.name} reaches for its weapon...")
    print("Wait for DRAW, then press Enter!")

    delay = random.uniform(1.5, 4.0)
    time.sleep(delay)

    print("\nDRAW!")
    start = time.time()
    input("> ")
    reaction_time = time.time() - start

    if reaction_time <= 0.35:
        damage = int(player.attack * 2.5)
        target.health -= damage
        return f"Perfect draw! You blast the {target.name} for {damage} damage!"

    elif reaction_time <= 0.75:
        damage = int(player.attack * 1.5)
        target.health -= damage
        return f"Good shot! You hit the {target.name} for {damage} damage."

    else:
        damage = player.attack
        target.health -= damage
        return f"Too slow, but you still fire! The {target.name} takes {damage} damage."
    

def use_beats(player, enemies):
    target = next((e for e in enemies if e.is_alive), None)
    if not target:
        return "There is nothing to drop the beat on."

    notes = ["a", "s", "d", "f"]
    sequence = [random.choice(notes) for _ in range(5)]

    hits = 0
    window = 0.75  # seconds allowed per note

    print("\nBeats Rhythm Chain!")
    print("Press each key as it appears. No Enter needed.")
    print("Get ready...")
    time.sleep(1.5)

    for note in sequence:
        print(f"\n>>>  {note.upper()}  <<<")
        start = time.time()
        pressed = None

        while time.time() - start < window:
            if msvcrt.kbhit():
                pressed = msvcrt.getch().decode("utf-8").lower()
                break
            time.sleep(0.01)

        if pressed == note:
            hits += 1
            print("Hit!")
        elif pressed is None:
            print("Miss!")
        else:
            print(f"Wrong key! You pressed {pressed.upper()}.")

        time.sleep(0.25)

    accuracy = hits / len(sequence)

    if accuracy == 1:
        damage = int(player.attack * 2.5)
        target.health -= damage
        return f"Perfect combo! The beat crushes the {target.name} for {damage} damage!"

    elif accuracy >= 0.8:
        damage = int(player.attack * 1.8)
        target.health -= damage
        return f"Great rhythm! The {target.name} takes {damage} damage."

    elif accuracy >= 0.5:
        damage = player.attack
        target.health -= damage
        return f"You keep the rhythm alive! The {target.name} takes {damage} damage."

    else:
        return "You lose the beat. No effect."
    

def use_defuse(player, enemies):
    target = next((e for e in enemies if e.is_alive), None)
    if not target:
        return "There is nothing to defuse."

    wires = ["red", "blue", "green", "yellow"]
    safe_wire = random.choice(wires)
    clues = {
        "red": ["The hot wire would get you ejected in soccer.", "The safe current runs hot.", "Cut the wire the color of blood."],
        "blue": ["The safe current runs cold.", "Cut the wire the color of the sky.", "The safe wire is feeling sad."],
        "green": ["Cut the wire the color of old circuit boards.", "The safe wire is the color of envy.", "You wouldn't like the safe wire when it's angry."],
        "yellow": ["Cut the banana flavored wire.", "The safe wire shines bright like the sun.", "Two of these get's you a red card."]
    }
    clue = random.choice(clues[safe_wire])

    clues = {
        "red": ["The hot wire would get you ejected in soccer.", "The safe current runs hot.", "Cut the wire the color of blood."],
        "blue": ["The safe current runs cold.", "Cut the wire the color of the sky.", "The safe wire is feeling sad."],
        "green": ["Cut the wire the color of old circuit boards.", "The safe wire is the color of envy.", "You wouldn't like the safe wire when it's angry."],
        "yellow": ["Cut the banana flavored wire.", "The safe wire shines bright like the sun.", "Two of these get's you a red card."]
    }

    print("\nDefuse!")
    print("A volatile charge begins to pulse...")
    print("Choose the correct wire before it detonates!\n")
    print("[1] Red")
    print("[2] Blue")
    print("[3] Green")
    print("[4] Yellow")
    print()
    print(f"Clue: {clue}")

    time_limit = 5
    choice = ""

    print("\nCut wire: ", end="", flush=True)
    start = time.time()

    while time.time() - start < time_limit:
        remaining = time_limit - int(time.time() - start)

        print(f"\rTime left: {remaining}s | Cut wire: {choice}", end="", flush=True)

        if msvcrt.kbhit():
            key = msvcrt.getch().decode("utf-8").lower()

            if key == "\r":  # Enter
                break
            elif key == "\b":  # Backspace
                choice = choice[:-1]
            else:
                choice += key

        time.sleep(0.05)

    print()

    wire_map = {
        "1": "red",
        "red": "red",
        "r": "red",
        "2": "blue",
        "blue": "blue",
        "b": "blue",
        "3": "green",
        "green": "green",
        "g": "green",
        "4": "yellow",
        "yellow": "yellow",
        "y": "yellow",
    }

    chosen_wire = wire_map.get(choice)

    if chosen_wire == safe_wire:
        damage = int(player.attack * 2.75)
        target.health -= damage
        return f"Wire cut cleanly! The charge redirects into the {target.name} for {damage} damage!"

    backlash = max(1, int(player.max_health * 0.15))
    player.take_damage(backlash)
    return f"Wrong wire! The charge backfires and you take {backlash} damage."