import numpy as np

class KnowledgeCost:
    tier_1 = 0.15
    tier_2 = 0.40
    tier_3 = 0.75
    tier_4 = 0.95

def cast_entropy(comprehension: float) -> float:
    # shannon entropy = casting uncertainty
    # H(p) = -p * log2(p) - (1-p) * log2(1-p)
    p = np.clip(comprehension, 1e-15, 1.0 - 1e-15)
    return round(float(-p*np.log2(p) - (1.0-p) * np.log2(1.0-p)), 4)

def comp2probability(comprehension: float) -> float: # calc base success
    entropy = cast_entropy(comprehension)
    return float(1.0 - (entropy * 0.7))

def school_entropy(school: bool, base_comp: float) -> float:
    # being in school decreases the entropy
    if school:
        effect = np.clip(base_comp * 1.35, 0.0, 1.0)
        return cast_entropy(effect)

# —— TEST for file
if __name__ == "__main__":
    print(cast_entropy(0.9))
    print(comp2probability(0.9))
    print(school_entropy(True, 0.9))