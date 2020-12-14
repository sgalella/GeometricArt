import time as time

import numpy as np
from PIL import ImageChops


def compute_similarity(target, output, max_difference):
    """
   Compares the target and the generated image.

    Args:
        target (np.array): Objective image.
        output (np.array): Image generated randomly.
        max_difference (int): Maximum possible difference.

    Returns:
        float: Difference between the images (in the range between 0 and 1).
    """
    difference = np.sum(ImageChops.difference(target, output))
    similarity = 100 * (1 - (difference / max_difference))
    return similarity


def get_time_elapsed(start):
    """
    Calculates the time elapsed of the algorithm.

    Args:
        start (time): Onset of timer.

    Returns:
        tuple: Values of time split in hours, minutes and seconds.
    """
    end = time.time()
    seconds = round(end - start)
    hours, seconds = seconds // 3600, seconds % 3600
    minutes, seconds = seconds // 60, seconds % 60
    return hours, minutes, seconds
