# Adapted from https://gitlab.com/ddorn/brocoli/-/blob/master/brocoli/processing/colors.py

from colorsys import rgb_to_hsv, hsv_to_rgb

import numpy as np
import pygame

__all__ = ["gradient"]


def mix(a, b, f):
    return [round(aa * (1 - f) + bb * f) for aa, bb in zip(a, b)]


def hsv_mix(a, b, f):
    if abs(a[0] - b[0]) < 0.5:
        h = a[0] * (1 - f) + b[0] * f
    elif a[0] > b[0]:
        h = (a[0] * (1 - f) + (b[0] + 1) * f) % 1
    else:
        h = (a[0] * (1 - f) + (b[0] - 1) * f) % 1

    s = a[1] * (1 - f) + b[1] * f
    v = a[2] * (1 - f) + b[2] * f
    if len(a) == 4:
        alpha = (a[3] * (1 - f) + b[3] * f,)
    else:
        alpha = ()

    return (h, s, v, *alpha)


def hsv_to_RGB(h, s, v, *a):
    r, g, b = hsv_to_rgb(h, s, v)
    return [int(255 * _) for _ in (r, g, b, *a)]


def RGB_to_hsv(r, g, b, *a):
    a = [_ / 255 for _ in a]
    return (*rgb_to_hsv(r / 255, g / 255, b / 255), *a)


def gradient(*colors, steps, loop=False):
    """
    Yield the values of a colorisation as RGB tuple.
    :param colors: RGB tuples or hex strings
    :param steps: number of colors to generate
    """
    assert len(colors) >= 2, "There should be at least two colors in a gradient"
    colors = [pygame.Color(c) for c in colors]

    if loop:
        colors.append(colors[0])

    colors = [RGB_to_hsv(*c) for c in colors]

    nb_segments = len(colors) - 1
    a = colors[0]
    b = colors[1]
    segment = 1
    grad = np.zeros((steps, max(map(len, colors))))
    for i in range(steps):
        pos = i / (steps - 1)
        if pos > segment / nb_segments:
            segment += 1
            a, b = b, colors[segment]
        seg_pos = f = pos * nb_segments - (segment - 1)

        if abs(a[0] - b[0]) < 1 / 3 and abs(a[2] - b[2]) < 1.0 / 2:
            grad[i] = hsv_to_RGB(*hsv_mix(a, b, f))
        else:
            grad[i] = mix(hsv_to_RGB(*a), hsv_to_RGB(*b), seg_pos)

    # no alpha
    if np.all(grad[:, 3] == 255):
        return grad[:, :3]
    return grad
