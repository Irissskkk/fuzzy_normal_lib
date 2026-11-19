import random
from .fuzzy_normal import FuzzyNormal
from .fuzzy_set import FuzzySet


def generate_set(n: int = 200, x0_range=(-5, 5), sigma_range=(0.5, 2.0)) -> FuzzySet:
    """Генерирует n нечётких нормальных величин со случайными параметрами."""
    if not (100 <= n <= 300):
        raise ValueError("Количество величин должно быть 100..300")
    fs = FuzzySet()
    for i in range(n):
        x0 = random.uniform(*x0_range)
        sigma = random.uniform(*sigma_range)
        fs.add(FuzzyNormal(x0, sigma, name=f"FV_{i:03d}"))
    return fs
