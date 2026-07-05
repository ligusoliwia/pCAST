import numpy as np
from enum import Enum, auto
from typing import Optional
import json
import os

class PeriodicTable(Enum):
    EUHERIA = auto() #air, the element of freedom
    EXELIS = auto() #water, the element of change
    KRATOS = auto() #fire, the element of power
    STASIS = auto() #earth, the element of stability
    PHOS = auto() #light, the element of energy
    KHOROS = auto() #chaos, the element of entropy

class AffinityMatrix:
    def __init__(self):
        self.elements = list(PeriodicTable)

        self.matrix = np.array([
            #EUHERIA     EXELIS   KRATOS   STASIS   PHOS     KHOROS
            1.4,         0.8,     1.1,     0.2,     0.6,     1.3,  #EUHERIA caster
            0.6,         1.4,     0.2,     0.8,     1.3,     1.1,  #EXELIS caster
            1.1,         0.2,     1.4,     0.6,     1.3,     1.1,  #KRATOS caster
            0.2,         0.6,     0.6,     1.4,     0.6,     0.8,  #STASIS caster
            1.3,         1.1,     1.3,     0.6,     1.4,     0.2,  #PHOS caster
            0.8,         1.0,     1.3,     0.8,     0.2,     1.4,  #KHOROS caster
        ], dtype=float)

        # ranges:
            # 1.4 → perfect synergy
            # 1.3 → strong synergy (elements fuel each other)
            # 1.1 → mild synergy (compatible)
            # 1.0 → neutral
            # 0.8 → mild friction (opposing tendencies)
            # 0.6 → strong friction (completly different natures)
            # 0.2 → conflict (oposite elements, these destroy each other)
        
        self.conflicts = {
        frozenset([PeriodicTable.EXELIS,  PeriodicTable.KRATOS]),
        frozenset([PeriodicTable.STASIS,  PeriodicTable.KHOROS]),
        frozenset([PeriodicTable.PHOS,    PeriodicTable.KHOROS]),
        frozenset([PeriodicTable.EUHERIA, PeriodicTable.STASIS])
        }

    def affinity(self, caster: PeriodicTable, spell: PeriodicTable) -> float:
        c = caster.value - 1
        s = spell.value - 1
        return self.matrix[c, s]