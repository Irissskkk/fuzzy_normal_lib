"""Кластерный анализ множества нечётких величин (k-means)"""
import random
import math
from .fuzzy_set import FuzzySet


def _dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def kmeans(fuzzy_set: FuzzySet, k: int = 3, max_iter: int = 100):
    points = [(fv.x0, fv.sigma) for fv in fuzzy_set]
    n = len(points)
    if k <= 0 or k > n:
        raise ValueError("k должно быть в диапазоне 1..N")

    centroids = random.sample(points, k)
    labels = [-1] * n

    for _ in range(max_iter):
        new_labels = [min(range(k), key=lambda j: _dist(p, centroids[j]))
                      for p in points]
        if new_labels == labels:
            break
        labels = new_labels

        for j in range(k):
            cluster_pts = [points[i] for i in range(n) if labels[i] == j]
            if cluster_pts:
                cx = sum(p[0] for p in cluster_pts) / len(cluster_pts)
                cy = sum(p[1] for p in cluster_pts) / len(cluster_pts)
                centroids[j] = (cx, cy)

    clusters = [[] for _ in range(k)]
    for i, fv in enumerate(fuzzy_set):
        clusters[labels[i]].append(fv)
    return clusters
'''выделить подмножество из множества добавить, картинка до применения альфа и после, ссылка на реопзиторий, маметматика solution развертка'''