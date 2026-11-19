"""Нечёткая величина с нормальной функцией принадлежности."""
import math
import random


class FuzzyNormal:
    """
    Нечёткая величина N(x0, sigma).
    Функция принадлежности:
        phi(x) = 1/(sqrt(2*pi)*sigma) * exp(-(x-x0)^2/(2*sigma^2))
    """

    def __init__(self, x0: float = 0.0, sigma: float = 1.0, name: str = ""):
        if sigma <= 0:
            raise ValueError("sigma должна быть > 0")
        self.x0 = float(x0)
        self.sigma = float(sigma)
        self.name = name or f"N({x0:.2f},{sigma:.2f})"

    def membership(self, x: float) -> float:
        return (1.0 / (math.sqrt(2 * math.pi) * self.sigma)) * \
               math.exp(-((x - self.x0) ** 2) / (2 * self.sigma ** 2))

    def max_membership(self) -> float:
        """Максимальное значение функции принадлежности (в точке x0)."""
        return 1.0 / (math.sqrt(2 * math.pi) * self.sigma)

    def alpha_cut(self, alpha: float):
        max_mu = self.max_membership()
        if alpha > max_mu:
            return None
        if alpha <= 0:
            return (float('-inf'), float('inf'))
        
        # Решаем уравнение: alpha = max_mu * exp(-(x-x0)^2 / (2*sigma^2))
        # => x = x0 +/- sigma * sqrt(2 * ln(max_mu / alpha))
        delta_x = self.sigma * math.sqrt(2 * math.log(max_mu / alpha))
        return (self.x0 - delta_x, self.x0 + delta_x)

    @staticmethod
    def _standard_normal(n: int = 10) -> float:
        w = random.gauss(0.0, 1.0)
        return w - (1.0 / (20 * n)) * (w ** 3 - 3 * w)

    def sample(self, n: int = 10) -> float:
        return self.sigma * self._standard_normal(n) + self.x0

    def __add__(self, other):
        if isinstance(other, FuzzyNormal):
            return FuzzyNormal(self.x0 + other.x0,
                               math.sqrt(self.sigma ** 2 + other.sigma ** 2))
        return FuzzyNormal(self.x0 + other, self.sigma)

    def __sub__(self, other):
        if isinstance(other, FuzzyNormal):
            return FuzzyNormal(self.x0 - other.x0,
                               math.sqrt(self.sigma ** 2 + other.sigma ** 2))
        return FuzzyNormal(self.x0 - other, self.sigma)

    def __mul__(self, other):
        if isinstance(other, FuzzyNormal):
            x0 = self.x0 * other.x0
            sigma = math.sqrt((self.x0 ** 2) * (other.sigma ** 2) +
                              (other.x0 ** 2) * (self.sigma ** 2))
            return FuzzyNormal(x0, max(sigma, 1e-9))
        return FuzzyNormal(self.x0 * other, abs(self.sigma * other))

    def __truediv__(self, other):
        if isinstance(other, FuzzyNormal):
            if abs(other.x0) < 1e-9:
                raise ZeroDivisionError("Деление на нечёткую величину с x0≈0")
            x0 = self.x0 / other.x0
            sigma = math.sqrt((self.sigma ** 2) / (other.x0 ** 2) +
                              (self.x0 ** 2) * (other.sigma ** 2) / (other.x0 ** 4))
            return FuzzyNormal(x0, max(sigma, 1e-9))
        if abs(other) < 1e-12:
            raise ZeroDivisionError
        return FuzzyNormal(self.x0 / other, self.sigma / abs(other))

    def __eq__(self, other):
        return isinstance(other, FuzzyNormal) and \
               abs(self.x0 - other.x0) < 1e-9 and abs(self.sigma - other.sigma) < 1e-9

    def __lt__(self, other):
        return self.x0 < (other.x0 if isinstance(other, FuzzyNormal) else other)

    def __repr__(self):
        return f"FuzzyNormal(x0={self.x0:.4f}, sigma={self.sigma:.4f})"

    def to_dict(self):
        return {"x0": self.x0, "sigma": self.sigma, "name": self.name}

    @classmethod
    def from_dict(cls, d):
        return cls(d["x0"], d["sigma"], d.get("name", ""))

    def sample_statistics(self, n_samples: int = 100):
        samples = [self.sample() for _ in range(n_samples)]
        mean_x = sum(samples) / n_samples
        if n_samples > 40:
            var_s = sum(x**2 for x in samples) / n_samples - mean_x**2
        else:
            var_s = sum((x - mean_x)**2 for x in samples) / (n_samples - 1)
        std_s = var_s ** 0.5
        return {
            "mean": mean_x,
            "variance": var_s,
            "std": std_s,
            "samples": samples
        }
