# all the info on magic casters :) TODO
import json
from elements import (PeriodicTable, ArcaneSchool, SCHOOL_ELEMENTS, AffinityMatrix)
from dataclasses import dataclass
import os

class SchoolMembership:
    school_id: str
    elements: tuple[PeriodicTable, PeriodicTable]
    proficiency: float = 0.0 # grows with use from 0 - 1
    joined_at: float = 0.0 # simulation time

class Caster:
    # attributes

    # properties

    # casting

    # progression

    # recovery
    pass