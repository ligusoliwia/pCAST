from dataclasses import dataclass
from elements import PeriodicTable
import json

@dataclass
class Spell:
    name: str
    element: PeriodicTable
    tier: int # 1- 4
    mana_cost: float
    cast_time: float # in seconds
    base_difficulty: float
    conflict_risk: bool
    description: str

def load_grimoire(path: str) -> list[Spell]:
    with open(path, "r") as spell_book:
        data = json.load(spell_book)
    return [parse_spell(s) for s in data if s.get("name")]
    
def parse_spell(spell: dict) -> Spell:
    return Spell(
        name = spell["name"],
        element = PeriodicTable[spell["element"]],
        tier = spell["tier"],
        mana_cost = spell["mana_cost"],
        cast_time = spell["cast_time"],
        base_difficulty = spell["base_difficulty"],
        conflict_risk = spell["conflict_risk"],
        description = spell.get("description", "") # in case desc doesn't exist
    )

# TEST
if __name__ == "__main__":
    grimoire = load_grimoire("grimoire.json")
    for spell in grimoire:
        print(f"{spell.name:<20} tier {spell.tier}  {spell.element.name}  {spell.mana_cost} mana")