# imports
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
from random import random

# failures
class FailureType(Enum):
    FIZZLE = auto() # spell doesn't fire at all
    BACKFIRE = auto() # spell unstable & energy hits the caster
    OVERCAST = auto() # uncontrolled release of energy
    COLLAPSE = auto() # catastrophic failure
    DESYNC = auto() # conflicting elements fighting each other

BASE_PROBABILITY = 0.9

# modifier recorder
class ModifierChain:
    def __init__(self, spell_name: str, caster_name: str):
        self.spell_name = spell_name
        self.caster_name = caster_name
        self._storage: list[tuple[str, float, float]] = []
                                # label, modifier value, running total
        self._running: float = BASE_PROBABILITY
    
    def add(self, label: str, modifier: float) -> "ModifierChain":
        self._running *= modifier
        self._storage.append((label, modifier, round(self._running, 3)))
        return self

    def apply(self) -> float:
        return round(self._running, 3)
    
    def breakdown(self) -> str: # prings the list
        lines = []
        lines.append(f"spell: {self.spell_name}")
        lines.append(f"caster: {self.caster_name}")
        lines.append(f"base probability: {BASE_PROBABILITY}")
        for i, (label, modifier, running) in enumerate(self._storage):
            lines.append(f"{label:<20} {modifier:>6.3f} → {running:.4f}")
        lines.append(f"final: {self.apply():>28.4f}")
        return "\n".join(lines)
    
@dataclass
class CastResult:
    success: bool # did the spell succeed?
    final_probability: float # return from chain.apply()
    rolled: float
    failure_type: Optional[FailureType]
    chain_log: ModifierChain
    conflicted: bool = False

# cast resolver
class CastResolver:
    def __init__(self,
                 fizzle: float = 0.45,
                 backfire: float = 0.30,
                 overcast: float = 0.20,
                 collapse: float = 0.15,
                 desync: float = 0.40):
        self.fizzle = fizzle
        self.backfire = backfire
        self.overcast = overcast
        self.collapse = collapse
        self.desync = desync

    def classify_failure(self, probability: float) -> FailureType:
        if probability >= self.fizzle: return FailureType.FIZZLE
        if probability >= self.backfire: return FailureType.BACKFIRE
        if probability >= self.overcast: return FailureType.OVERCAST
        return FailureType.COLLAPSE

    def resolve(self, chain: ModifierChain, conflicted: bool = False) -> CastResult:
        probability = chain.apply()
        roll = random()
        success = roll < probability

        # for conflicted elements:
        if success and conflicted:
            self.desync_chance = (1.0 - (roll / probability)) * self.desync
            if random() < self.desync_chance:
                return CastResult(
                    success = False,
                    final_probability = probability,
                    rolled = roll,
                    failure_type = FailureType.DESYNC,
                    chain_log = chain,
                    conflicted = True
                )
            
        # for regular outcomes:
        return CastResult(
                    success = success,
                    final_probability = probability,
                    rolled = roll,
                    failure_type = None if success else self.classify_failure(probability),
                    chain_log = chain,
                    conflicted = conflicted
                )
    
# TEST
if __name__ == "__main__":
    # 1. build the chain
    chain = (
        ModifierChain(spell_name="Fireball", caster_name="Aldric")
        .add("skill",     1.30)
        .add("affinity",  1.40)
        .add("fatigue",   0.70)
        .add("humidity",  0.40)
    )

    # 2. print the breakdown
    print(chain.breakdown())

    # 3. resolve it
    resolver = CastResolver()
    result   = resolver.resolve(chain, conflicted=False)

    # 4. read the result
    print(result.success)           # True or False
    print(result.rolled)            # e.g. 0.31
    print(result.final_probability) # e.g. 0.42
    print(result.failure_type)      # None or FailureType.FIZZLE etc.