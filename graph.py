import math


def perendicular_line(b1, b2):
    """Get a line function that is perendicular to the line between the 2 buds.

    The resulting function goes through b2' center + an offset that moves the line behind
    b2 (away from b1).

    :param Bud b1: the first bud
    :param Bud b2: the second bud
    :rtype: function
    :return: the line function
    """
    if b1.angle2x(b2.angle - b1.angle) == 0:
        sign = (b1.height - b2.height)/abs(b1.height - b2.height)
        return lambda bud: b2.height + sign * b2.scale/2

    m = (b2.height - b1.height) / b1.angle2x(b2.angle - b1.angle)
    x = b1.height - b2.height
    offset = b2.scale * 4 * x/abs(x)
    return lambda b: -1 / m * b.angle2x(b.angle - b1.angle) + b1.height - offset


def inner_tangents(b1, b2):
    """Get the inner tangents between the given buds.

    :param Bud b1: the first bud
    :param Bud b2: the second bud
    :rtype: (function, function)
    returns: line functions representing the tangents
    """
    xp = (b1.angle2x(b2.angle - b1.angle) * b1.scale) / ((b1.scale + b2.scale) * b1.radius)
    yp = (b2.height * b1.scale + b1.height * b2.scale) / (b1.scale + b2.scale)

    worldxp, b, r = b1.angle2x(xp), b1.height, b1.scale
    sqrd = math.sqrt(worldxp**2 + (yp - b)**2 - r**2)
    absd = abs(worldxp**2 + (yp - b)**2)
    x1 = ((r**2) * worldxp + r * (yp - b) * sqrd) / (absd * b1.radius)
    x2 = ((r**2) * worldxp - r * (yp - b) * sqrd) / (absd * b1.radius)

    y1 = ((r**2) * (yp - b) - r * worldxp * sqrd) / absd + b
    y2 = ((r**2) * (yp - b) + r * worldxp * sqrd) / absd + b

    left = lambda b: ((yp - y1) * b.angle2x(b.angle - b1.angle - x1)) / b.angle2x(xp - x1) + y1
    right = lambda b: ((yp - y2) * b.angle2x(b.angle - b1.angle - x2)) / b.angle2x(xp - x2) + y2
    return left, right


def get_reachable(selected, buds):
    """Filter the given buds for all that can be accessed by the selected bud without collisions.

    :param Bud selected: The selected bud
    :param list buds: all available buds
    :returns: a list of accessible buds.
    """
    if not buds:
        return []

    tested, filtered = buds[0], []

    # Check whether the 2 bud circles are intersecting
    if selected.distance(tested) <= selected.scale + tested.scale:
        # the circles are intersecting, so get a line perendicular to the tested bud. Any buds
        # behind the line are discarded. An offset it used to move the line a bit backwards, as
        # otherwise the check is a bit too strict
        left = perendicular_line(selected, tested)
        for bud in buds[1:]:
            if selected.height < tested.height:
                if left(bud) < bud.height:
                    continue
            elif left(bud) >= bud.height:
                continue
            filtered.append(bud)
    else:
        # The circles are disjoint - get the inner tangents of the 2 circles - any point that
        # lies behind the tested bud, but between the 2 tangents can be safely discarded.
        left, right = inner_tangents(selected, tested)

        # filter out any buds that cannot be accessed without any collisions. The `if` magic below
        # is because checking if a point lies above or below the `left` and 'right` lines is dependant
        # on where the tested point lies relative to the selected bud.
        # WARNING! Any modifications of the following code should be thoroughly tested!
        for bud in buds[1:]:
            if left(tested) >= tested.height:
                if right(tested) >= tested.height:
                    if left(bud) >= bud.height and right(bud) >= bud.height:
                        continue
                elif left(bud) >= bud.height and right(bud) < bud.height:
                    continue
            elif left(bud) < bud.height:
                if right(tested) >= tested.height:
                    if right(bud) >= bud.height:
                        continue
                elif right(bud) < bud.height:
                    continue
            filtered.append(bud)
    return [tested] + get_reachable(selected, filtered)

