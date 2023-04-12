#############################################################################
##
##                       UTILITY FUNCTIONS (utils.py)
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from functools import wraps
from time import perf_counter


# MISC =====================================================================

def timer(func):
    """
    shows the execution time 
    of the function object passed
    """
    def wrap_func(*args, **kwargs):

        t1 = perf_counter()
        result = func(*args, **kwargs)
        t2 = perf_counter()

        print(f'Function {func.__name__!r} executed in {(t2-t1)*1e3:.2f}ms')

        return result

    return wrap_func


def point_inside_polygon(position, polygon):
    """
    ray casting algorithm to check 
    if point is in polygon
    """
    x, y = position
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersect = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= x_intersect:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def boundingbox_from_shape(polygon):
    """
    compute the rectangular bounding box 
    of the polygon shape
    """
    pts_x, pts_y = zip(*polygon)
    return max(pts_x), min(pts_x), max(pts_y), min(pts_y)
