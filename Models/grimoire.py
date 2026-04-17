class Grimoire:
    def __init__(self, name, description, spells):
        self.name = name
        self.description = description
        self.spells = spells        # list of Spell objects, all locked initially
        self.unlocked_spells = []   # spells the player can actually cast

    def gain_insight(self, examine_target):
        """Called whenever the player examines something.
        Checks if any locked spell should unlock based on this target."""
        for spell in self.spells:
            if spell not in self.unlocked_spells:
                if examine_target in spell.unlock_triggers:
                    self.unlocked_spells.append(spell)
                    return f"A passage in the grimoire becomes clear... You've learned {spell.name}!"
        return None

    def get_spell(self, spell_name):
        """Returns unlocked spell by name, or None."""
        return next((s for s in self.unlocked_spells 
                     if s.name.lower() == spell_name.lower()), None)

    def list_spells(self):
        if not self.unlocked_spells:
            return "The grimoire's pages are still indecipherable."
        return "Known spells:\n" + "\n".join(
            f"- {s.name} (Cost: {s.mana_cost} MP, Damage: {s.damage})" 
            for s in self.unlocked_spells
        )