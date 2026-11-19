"""Множество нечётких величин + операции над множествами."""
from .fuzzy_normal import FuzzyNormal


class FuzzySet:
    def __init__(self, items=None):
        self.items = list(items) if items else []

    def add(self, fv: FuzzyNormal):
        self.items.append(fv)

    def remove(self, index: int):
        self.items.pop(index)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def _pairwise(self, other, op):
        if len(self) != len(other):
            raise ValueError("Множества должны быть одной длины")
        return FuzzySet([op(a, b) for a, b in zip(self.items, other.items)])

    def __add__(self, other):
        return self._pairwise(other, lambda a, b: a + b)

    def __sub__(self, other):
        return self._pairwise(other, lambda a, b: a - b)

    def __mul__(self, other):
        return self._pairwise(other, lambda a, b: a * b)

    def __truediv__(self, other):
        return self._pairwise(other, lambda a, b: a / b)

    def to_list(self):
        return [fv.to_dict() for fv in self.items]

    @classmethod
    def from_list(cls, lst):
        return cls([FuzzyNormal.from_dict(d) for d in lst])
