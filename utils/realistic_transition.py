from random import random

from utils.gisaug.augmentations import Stretch


def realistic_transition(y1: [float], y2: [float]) -> ([float], [float]):
    if len(y1) < 2 or len(y2) < 2:
        return list(y1), list(y2)

    y1min, y2min, y1max, y2max = min(y1), min(y2), max(y1), max(y2)
    if y1min == y1max or y2min == y2max:
        return list(y1), list(y2)

    drop_point_per = 0.1 * (max(y1max, y2max) - min(y1min, y2min)) / max(y1max - y1min, y2max - y2min)
    save_point_per = 1 - drop_point_per if drop_point_per < 0.5 else 0.5
    y_a, y_b = list(Stretch.stretch_curve(y1, save_point_per)), list(Stretch.stretch_curve(y2, save_point_per))

    average, start_value = y_b[0] - y_a[-1], y_a[-1]
    len_dist = len(y1) + len(y2) - len(y_a) - len(y_b) + 1

    step: () = lambda ind, l: average * ((random() / 2) * (1 - ind / l) + ind / l)
    middle = [start_value + step(ind, len_dist) for ind in range(1, len_dist)]
    y = y_a + middle + y_b

    offset_value = int(len(y) / 2)

    y_a = Stretch.stretch_curve_by_count(y[0:offset_value], len(y1))
    y_b = Stretch.stretch_curve_by_count(y[offset_value:], len(y2))
    return list(y_a), list(y_b)