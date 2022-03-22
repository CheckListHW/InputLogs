import numpy as np

from resourses.limits import MAX_TREND_RATIO


def ceil(i: float) -> float:
    return i if -MAX_TREND_RATIO <= i <= MAX_TREND_RATIO else np.sign(i) * MAX_TREND_RATIO
