import math

from magnolia.meristem import Bud
from magnolia.math.geometry import norm_angle, cross_product, vect_mul, length, in_cone_checker


def dir_vector(b1: Bud, b2: Bud) -> tuple:
    """Return a direction vector for the provided buds."""
    return (norm_angle(b1.angle - b2.angle), b1.height - b2.height, b1.radius - b2.radius)


def line_distance_check(b1, b2):
    """Return a function that calculates the distance from a line between the provided buds."""
    # the direction vector between the buds
    dir_vec = dir_vector(b1, b2)

    def checker(bud):
        # the diff between b1 and bud
        diff = (norm_angle(bud.angle - b1.angle), bud.height - b1.height, bud.radius - b1.radius)

        return length(cross_product(diff, dir_vec)) / length(dir_vec)

    return checker


def middle_point(b1, b2):
    """Find the approximate cutting point of the inner tangents of the provided buds."""
    dir_vec = dir_vector(b2, b1)
    line_len = length(dir_vec)

    normed_dir = vect_mul(dir_vec, 1/line_len)

    d1 = (b1.scale * line_len) / (b1.scale + b2.scale)

    return (
        norm_angle(b1.angle + d1 * normed_dir[0]),
        b1.height + d1 * normed_dir[1],
        b1.radius + d1 * normed_dir[2],
    )


def occlusion_cone(b1, b2):
    """Return a function that tests whether a given bud lies in the occlusion cone behind b2 from b1."""
    dir_vec = dir_vector(b2, b1)
    apex = middle_point(b1, b2)

    # because of the overwrapping of angles, there is a degenerative case when the cone lies on the angle axis
    if dir_vec[1] == 0 and dir_vec[2] == 0:
        h = length((norm_angle(b2.angle - apex[0]), b2.height - apex[1], b2.radius - apex[2]))
    else:
        h = length((norm_angle(b2.angle - apex[0]), b2.height - apex[1], b2.radius - apex[2]))
    return in_cone_checker(apex, dir_vec, b2.scale, h)


def on_helix_checker(b1, b2):
    """Return a function that checks if a bud lies on the helix going through the provided buds."""
    hdiff = b2.height - b1.height
    adiff = norm_angle(b2.angle - b1.angle)

    if b2.height < b1.height:
        hdiff = -hdiff
        adiff = -adiff

    # the buds are on the same height - a circle, not a helix
    if abs(hdiff) < 0.001:
        return lambda b: abs(b.height - b1.height) < 0.001

    # the buds have the same angle - a vertical line, not a helix
    if abs(adiff) < 0.001:
        return lambda b: abs(norm_angle(b.angle - b1.angle)) < 0.001

    slope = math.atan(adiff/hdiff)

    def on_helix(b):
        """Check if the provided bud is on the given helix.

        The helix is created as (bud.radius, t - bud.angle, slope*t - bud.height). This
        make things easier, as it's really just the unit helix moved up by the selected
        buds height, moved sideways by the selected buds angle and then streched so that
        it goes through the second bud. The slope is calculated from the tangent of how
        much the helix was moved laterly and vertically.
        """
        angle_diff = norm_angle(b.angle - b1.angle)
        height_diff = norm_angle(slope * (b.height - b1.height))
        return abs(angle_diff - height_diff) < min(1, abs(slope)) * b.scale

    return on_helix


def helix(b1, b2):
    """Return a generator that returns (cartesian) points on a helix going through the provided buds.

    Each point is b1.scale away from the next one.
    """
    hdiff = b2.height - b1.height
    adiff = norm_angle(b2.angle - b1.angle)

    # the buds are on the same height - a circle, not a helix
    if abs(hdiff) < 0.001:
        def circle(height):
            return (
                b1.cyl_to_cart(math.radians(a), b1.height, b1.radius + b1.scale)
                for a in range(0, 360, 5)
            )

        return circle

    # the buds have the same angle - a vertical line, not a helix
    if abs(adiff) < 0.001:
        def line(height):
            return (
                b1.cyl_to_cart(b1.angle, h, b1.radius + b1.scale)
                for h in range(int(round(height)))
            )

        return line

    slope = hdiff/adiff

    def helix_pos(height):
        """Check if the provided bud is on the given helix.

        The helix is created as (bud.radius, t - bud.angle, slope*t - bud.height). This
        make things easier, as it's really just the unit helix moved up by the selected
        buds height, moved sideways by the selected buds angle and then streched so that
        it goes through the second bud. The slope is calculated from the tangent of how
        much the helix was moved laterly and vertically.
        """
        # calculate the i which is closest to the origin. This is derived from
        #
        #   h(t) = slope * t + b1.height
        #   t(i) = sign *  i * math.radians(5)
        #   h(i) = slope * (sign *  i * math.radians(5)) + b1.height
        #   h(i) = 0
        i0 = int(round(-b1.height/(slope * math.radians(5))))

        # next calculate the i which is closest to the height (h(i) == height)
        iend = int(round((height - b1.height)/(slope * math.radians(5))))

        for i in range(min(i0, iend), max(i0, iend)):
            t = i * math.radians(5)
            angle, height, radius = norm_angle(t + b1.angle), slope * t + b1.height, b1.radius + b1.scale
            yield b1.cyl_to_cart(angle, height, radius)

    return helix_pos


def linear_function(b1, b2):
    """Get a linear function that goes through the given buds.

    This only works correctly when both are the same distance from the stella (i.e. they
    have the same radius).
    """
    if not b1.angle2x(b2.angle - b1.angle):
        # Handle invalid height linear functions.
        # As these functions are used to check if a bud is on a line, it suffices
        # to return the height of the given bud when the angle is the same, and in
        # other situations to return something that is totally off
        return lambda bud: bud.height if bud.angle == b1.angle else bud.height + 10000
    m = (b2.height - b1.height) / b1.angle2x(b2.angle - b1.angle)
    return lambda bud: m * bud.angle2x(bud.angle - b1.angle) + b1.height


def perendicular_plane_checker(b1, b2):
    """Return a function that checks if a bud is behind the plane perendicular to b2."""
    a, b, c = dir_vector(b1, b2)

    def checker(bud):
        """Return whether this bud is occluded by b2."""
        pl = a * norm_angle(bud.angle - b2.angle) + b * (bud.height - b2.height) + c * (bud.radius - b2.radius)
        return pl >= 0

    return checker
