# imports
from enum import Enum, auto
from typing import Dict, Optional, Tuple
import json

# —— MAGICAL RULES (world physics) ——

# types of magic, inheriting Enum prevents duplicates
class PeriodicTable(Enum):
    # main elements
    IGNIS = auto() # fire
    AQUA = auto()  # water
    AER = auto()   # air
    TERRA = auto() # earth
    LUX = auto()   # light
    ETER = auto()  # void

# loading arcane schools file (pure data)
def load_schools(path: str = "./arcane_schools.json"):
    with open(path, "r") as school_registry:
        return json.load(school_registry)

def build_school_enum(schools_data: list[dict]) -> type:
    return Enum("ArcaneSchool", {s["id"]: s["id"] for s in schools_data})

def build_school_elements(schools_data: list[dict], ArcaneSchool) -> dict:
    return {
        ArcaneSchool[s["id"]]: (
            PeriodicTable[s["elements"][0]],
            PeriodicTable[s["elements"][1]],
        )
        for s in schools_data
    }

_schools_data   = load_schools()
ArcaneSchool    = build_school_enum(_schools_data)
SCHOOL_ELEMENTS = build_school_elements(_schools_data, ArcaneSchool)

# elements interactions
class AffinityMatrix:
    def __init__(self):
        self._elemental_matrix: Dict[Tuple[PeriodicTable, PeriodicTable], float] = {}
        self._initialize_rules()
        # element conflicts:
        self.conflicts = {
            frozenset([PeriodicTable.IGNIS, PeriodicTable.AQUA]),
            frozenset([PeriodicTable.AER, PeriodicTable.TERRA]),
            frozenset([PeriodicTable.ETER, PeriodicTable.LUX])
        }

    # ———————————— element interactions ————————————
    def _initialize_rules(self):
        elements = [PeriodicTable.IGNIS, PeriodicTable.AQUA, PeriodicTable.AER, PeriodicTable.TERRA, PeriodicTable.LUX, PeriodicTable.ETER]

        # physics override; element / caster eg.: fire spell casted by fire mage has 1.4 multiplier etc. etc.
            # greater than 1.0 is a bonus and lower than 1.0 is a penalty (eg.: water mage casting fire lmao)
        for e1 in elements:
            for e2 in elements:
                if e1 == e2:
                    self._elemental_matrix[frozenset([e1, e2])] = 1.4
                else:
                    self._elemental_matrix[frozenset([e1, e2])] = 1.0

        # different elemental interactions:
        # 1.3 multiplier
        self._elemental_matrix[frozenset([PeriodicTable.IGNIS, PeriodicTable.LUX])]     = 1.3
        self._elemental_matrix[frozenset([PeriodicTable.AER, PeriodicTable.ETER])]      = 1.3
        self._elemental_matrix[frozenset([PeriodicTable.TERRA, PeriodicTable.AQUA])]    = 1.3
        
        # 1.1 multiplier
        self._elemental_matrix[frozenset([PeriodicTable.IGNIS, PeriodicTable.AER])]     = 1.1
        self._elemental_matrix[frozenset([PeriodicTable.TERRA, PeriodicTable.ETER])]    = 1.1
        self._elemental_matrix[frozenset([PeriodicTable.AQUA, PeriodicTable.LUX])]      = 1.1

        # 0.8 multiplier
        self._elemental_matrix[frozenset([PeriodicTable.TERRA, PeriodicTable.IGNIS])]   = 0.8
        self._elemental_matrix[frozenset([PeriodicTable.ETER, PeriodicTable.AQUA])]     = 0.8
        self._elemental_matrix[frozenset([PeriodicTable.AER, PeriodicTable.LUX])]       = 0.8

        # 0.6 multiplier
        self._elemental_matrix[frozenset([PeriodicTable.IGNIS, PeriodicTable.ETER])]    = 0.6
        self._elemental_matrix[frozenset([PeriodicTable.AER, PeriodicTable.AQUA])]      = 0.6
        self._elemental_matrix[frozenset([PeriodicTable.TERRA, PeriodicTable.LUX])]     = 0.6

        # 0.2 multiplier — the conflicted elements
        self._elemental_matrix[frozenset([PeriodicTable.AQUA, PeriodicTable.IGNIS])]    = 0.2
        self._elemental_matrix[frozenset([PeriodicTable.AER, PeriodicTable.TERRA])]     = 0.2
        self._elemental_matrix[frozenset([PeriodicTable.LUX, PeriodicTable.ETER])]      = 0.2

    def _get_modifier(self, caster_speciality: PeriodicTable, element: PeriodicTable) -> float:
        return self._elemental_matrix.get(frozenset([caster_speciality, element]), 1.0) # returns 1.0 if pair not in matrix

    # ———————————— calculations ————————————
    def calculate_affinity(self, caster_speciality: PeriodicTable, spell_element: PeriodicTable, arcane_school) -> float:
        # returns a single affinity multiplier (based on the interactions listed) for the ModifyChain

        base = self._elemental_matrix.get(frozenset([caster_speciality, spell_element]), 1.0)

        if arcane_school is None:
            # wild caster — no bonus, no penalty, just raw affinity
            return max(0.1, base)

        school_elements = SCHOOL_ELEMENTS[arcane_school]
        if spell_element in school_elements:
            # casting within speciality — school bonus
            return max(0.1, base * 1.25)
        else:
            # casting outside speciality — school penalty
            return max(0.1, base * 0.75)
    
    # ———————————— conflicts ————————————
    def is_conflicted(self, e1: PeriodicTable, e2: PeriodicTable) -> bool:
        return frozenset([e1, e2]) in self.conflicts
        # returns True when two elements face DESYNC

# ———————————— SPELL BOOK ————————————
# loading json grimoire
def load_grimoire(path: str) -> list[dict]:
    with open(path, "r") as spell_book:
        return json.load(spell_book)
    
def parse_spell(spell: dict) -> tuple[str, PeriodicTable, list[PeriodicTable]]:
    name = spell["name"]
    element = PeriodicTable[spell["element"]] # "FIRE" → PeriodicTable.FIRE
    return name, element

# ———————————— TEST ————————————
if __name__ == "__main__":
    matrix = AffinityMatrix()

    W = 42   # column width

    def header(title: str):
        print(f"\n{'─' * W}")
        print(f"  {title}")
        print(f"{'─' * W}")
        print(f"  {'caster':<18} {'spell':<12} {'affinity':>8}  {'note'}")
        print(f"  {'─'*18} {'─'*12} {'─'*8}  {'─'*14}")

    def row(caster_label, caster_el, spell_el, school=None):
        affinity   = matrix.calculate_affinity(caster_el, spell_el, school)
        conflicted = matrix.is_conflicted(caster_el, spell_el)
        school_str = f"[{school.name}]" if school else "[wild]"
        flag       = "⚠ conflict" if conflicted else ""
        print(f"  {caster_label:<18} {spell_el.name:<12} {affinity:>8.3f}  {flag}")


    # ── test 1: same-element casting ──────────────────────────────────────────────
    header("TEST 1 — same element casting (should all be high)")
    row("ignis  [wild]",  PeriodicTable.IGNIS, PeriodicTable.IGNIS)
    row("aqua   [wild]",  PeriodicTable.AQUA,  PeriodicTable.AQUA)
    row("aer    [wild]",  PeriodicTable.AER,   PeriodicTable.AER)
    row("terra  [wild]",  PeriodicTable.TERRA, PeriodicTable.TERRA)
    row("lux    [wild]",  PeriodicTable.LUX,   PeriodicTable.LUX)
    row("eter   [wild]",  PeriodicTable.ETER,  PeriodicTable.ETER)

    # ── test 2: school bonus vs wild ──────────────────────────────────────────────
    header("TEST 2 — school bonus vs wild (same spell)")
    row("ignis  [wild]",        PeriodicTable.IGNIS, PeriodicTable.IGNIS)
    row("ignis  [EVOCATION]",   PeriodicTable.IGNIS, PeriodicTable.IGNIS,  ArcaneSchool.EVOCATION)
    row("ignis  [ABJURATION]",  PeriodicTable.IGNIS, PeriodicTable.IGNIS,  ArcaneSchool.ABJURATION)
    row("ignis  [CONJURATION]", PeriodicTable.IGNIS, PeriodicTable.IGNIS,  ArcaneSchool.CONJURATION)

    # ── test 3: school penalty (casting outside speciality) ───────────────────────
    header("TEST 3 — school penalty (casting outside speciality)")
    row("lux [ILLUSION]  → lux",   PeriodicTable.LUX,   PeriodicTable.LUX,   ArcaneSchool.ILLUSION)
    row("lux [ILLUSION]  → ignis", PeriodicTable.LUX,   PeriodicTable.IGNIS, ArcaneSchool.ILLUSION)
    row("lux [ILLUSION]  → aqua",  PeriodicTable.LUX,   PeriodicTable.AQUA,  ArcaneSchool.ILLUSION)
    row("lux [ILLUSION]  → eter",  PeriodicTable.LUX,   PeriodicTable.ETER,  ArcaneSchool.ILLUSION)

    # ── test 4: conflict pairs ────────────────────────────────────────────────────
    header("TEST 4 — conflict pairs (should show ⚠ and low affinity)")
    row("ignis → aqua",  PeriodicTable.IGNIS, PeriodicTable.AQUA)
    row("aer   → terra", PeriodicTable.AER,   PeriodicTable.TERRA)
    row("eter  → lux",   PeriodicTable.ETER,  PeriodicTable.LUX)

    # ── test 5: full spell cast simulation ───────────────────────────────────────
    header("TEST 5 — fireball cast by different schools")
    spell = PeriodicTable.IGNIS
    for school in ArcaneSchool:
        els   = SCHOOL_ELEMENTS[school]
        label = f"{els[0].name}+{els[1].name} [{school.name[:6]}]"
        row(label, els[0], spell, school)

    print(f"\n{'─' * W}\n")
