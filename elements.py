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
    PHOS = auto() #light, the element of illumination
    KHOROS = auto() #chaos, the element of entropy

class AffinityMatrix:
    def __init__(self):
        self.elements = list(PeriodicTable)

        self.matrix = np.array([
            #EUHERIA     EXELIS   KRATOS   STASIS   PHOS     KHOROS
            [1.4,         1.0,     1.1,     0.2,     0.8,     1.1],  #EUHERIA caster
            [1.1,         1.4,     0.2,     1.1,     1.1,     1.1],  #EXELIS caster
            [1.3,         0.2,     1.4,     1.1,     1.3,     0.6],  #KRATOS caster
            [0.2,         0.8,     1.1,     1.4,     0.6,     1.3],  #STASIS caster
            [0.8,         1.1,     1.3,     0.8,     1.4,     0.2],  #PHOS caster
            [1.3,         1.3,     0.6,     1.3,     0.2,     1.4],  #KHOROS caster
        ], dtype=float)

        # ranges:
            # 1.4 >> perfect synergy
            # 1.3 >> strong synergy (elements fuel each other)
            # 1.1 >> mild synergy (compatible)
            # 1.0 >> neutral
            # 0.8 >> mild friction (opposing tendencies)
            # 0.6 >> strong friction (different natures)
            # 0.2 >> conflict (oposite elements, these destroy each other)
        
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
    
    def vector_affinity(self, caster_vector, spell_vector):
        result = caster_vector @ self.matrix @ spell_vector
        return result
    
    def dominant_element(self):
        eigenvalues, eigenvectors = np.linalg.eig(self.matrix)
        dominant_index = np.argmax(eigenvalues)
        dominant_vector = eigenvectors[:, dominant_index]
        
        scaling = np.abs(dominant_vector.real)
        ranking = sorted(
            zip(self.elements, scaling),
            key = lambda x: x[1],
            reverse = True 
        )
        return ranking

    def is_conflicted(self, e1: PeriodicTable, e2: PeriodicTable) -> bool:
        return frozenset([e1, e2]) in self.conflicts
    
if __name__ == "__main__":
    matrix = AffinityMatrix()
    print(matrix.matrix.shape)  #>> should print (6, 6)

    #pure EUHERIA caster casting pure EUHERIA spell >> should return 1.4
    euheria_caster = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    euheria_spell = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    print(matrix.vector_affinity(euheria_caster, euheria_spell))

    print("\ndominant element ranking:")
    for element, scale in matrix.dominant_element():
        bar = "█" * int(scale * 20)
        print(f"  {element.name:<10} {scale:.4f}  {bar}")
        