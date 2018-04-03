import math
import random
from typing import Tuple, List

from magnolia.meristem import Bud
from magnolia.graph import BudGraph
from magnolia.math.geometry import closest_circle, first_gap, front, check_collisions, cycle_ring, Sphere


class Positioner(BudGraph):

    BASE_RADIUS = 3.0

    def __init__(self, colour=(0, 0, 0.7), start_height=0, start_angle=0, size=None):
        """Initialise the positioner."""
        super().__init__()
        self.colour = colour
        self.bud_radius = size if size else self.BASE_RADIUS
        self.start_height = self.current_height = start_height
        self.start_angle = self.current_angle = start_angle

    def new(self):
        """Create a new item."""
        angle, height, radius, scale = self._next_pos()
        return Bud(
            radius=radius,
            height=height,
            angle=angle,
            scale=scale,
            fill_colour=self.colour,
        )

    def _next_pos(self) -> Tuple[Sphere, List[Sphere]]:
        """
        Get the position of the next item.

        This can be calculated according to various algorithms and based
        on the current state of the meristem.

        :rtype: tuple
        :returns: a tuple with the (position, front) of the next bud
        """
        return Sphere(0, 1, self.bud_radius, 1), None

    def n_positions(self, n):
        """Yield the positions of the next n buds."""
        for i in range(n):
            yield self._next_pos()

    def remove(self, item):
        """Remove the given item."""
        try:
            index = self.objects.index(item)
        except ValueError:
            # there is no such item - do nothing
            return

        self.objects = self.objects[:index] + self.objects[index + 1:]

    def move(self, item, index):
        """Move the provided item to the given index, moving all previous ones down."""
        if abs(index) > len(self.objects):
            return
        elif index < 0:
            index = len(self.objects) + index

        self.remove(item)
        self.objects = self.objects[:index] + [item] + self.objects[index:]

    def reset(self):
        """Reset the current position."""
        self.current_angle = self.start_angle
        self.current_height = self.start_height

    def recalculate(self, index=0):
        """Recalculate the positions of all items (starting from the provided index)."""
        self.reset()

        for item in self.objects[index:]:
            angle, height, radius, scale = self._next_pos()
            item.angle = angle
            item.height = height
            item.radius = radius
            item.scale = scale
        self._vertices = self.concat('vertices', self.displayables)

    @property
    def current_front(self):
        """Get the current front (the buds consisting the highest layer)."""
        return tuple()


class AnglePositioner(Positioner):

    def __init__(self, angle, n_per_row, **kwargs):
        super().__init__(**kwargs)
        self.angle = angle
        self.bud_radius = (math.pi * self.BASE_RADIUS) / n_per_row
        self.buds_per_row = n_per_row

        self._calc_steps()

    def _calc_steps(self):
        """
        Calculate lateral and vertical steps.


        If the angle is small, each bud can lie next to the next one, so the step is 2*R, where R is the radius
        of each bud in angle space. If the angle is greater than 45 degrees, the lateral step must be increased
        to avoid overlaps.
        The following diagram shows the calculations:

                                x
                        b3 ------------|
                      / | \            |
                    /   |   \         _|
                  /     |     \ d   -  |
                /       | h     \ /    |
              /         |         \  α |
            /           |           \  |
          /             |             \|
        b2 --------------------------- b1
                       2x

        2R = buds_per_layer / 2 * π
        d = 2R, as the new layer should touch the lower one, unless the angle is too big - then d should be scaled up
        x = R when α < 45° else x = sin(α) * d
        h = cos(α) * d
        """
        two_R = (2 * math.pi) / self.buds_per_row
        self.angle_step = two_R * math.sin(self.angle)
        self.lat_step = max(two_R, self.angle_step * 2)

        # the vertical step is in bud space, so it must be converted from angle space
        self.ver_step = 2 * self.bud_radius * math.cos(self.angle)

        self._current_row = 0

    def _next_pos(self) -> Tuple[Sphere, List[Sphere]]:
        """Calculate the position of the next bud."""
        self.current_angle += self.lat_step

        if self.current_angle > math.pi * 2:
            self._current_row += 1
            self.current_angle = (self._current_row * self.angle_step) % self.lat_step
            self.current_height += self.ver_step

        return Sphere(self.current_angle, self.current_height, self.BASE_RADIUS, self.bud_radius), None


class RingPositioner(Positioner):

    def __init__(self, angle, per_ring, height=None, **kwargs):
        """Initialise the positioner.

        :param double angle: the angle by which each ring should be rotated relative to the previous one
        :param int per_ring: how many buds per ring
        :param double height: the height between each ring. If not provided, the rings will touch each other
        """
        bud_radius = kwargs.pop('size', 0)
        if not bud_radius:
            bud_radius = (math.pi * self.BASE_RADIUS) / per_ring
        kwargs['size'] = bud_radius

        super().__init__(**kwargs)
        self.buds_per_ring = per_ring
        self.angle_step = 2 * math.pi / per_ring
        self.current_ring_place = self.current_ring = 0
        self.angle = angle
        self._height = height

    @property
    def ring_height(self):
        if self._height:
            return self._height

        # basic Pythagoras - lat is the lateral distance between 2 layers
        lat = abs(self.angle % self.angle_step)
        if lat > self.angle_step / 2:
            lat = self.angle_step - lat
        # scale up lat proportionally to the ring radius
        lat *= self.ring_radius
        return math.sqrt(abs(4*self.bud_radius**2 - lat**2))

    @property
    def ring_radius(self):
        """Return the radius of each ring."""
        return self.BASE_RADIUS

    def reset(self):
        """Reset the positioner."""
        super().reset()
        self.current_ring_place = self.current_ring = 0

    def _next_ring(self):
        """Move to the next ring."""
        self.current_ring += 1
        self.current_ring_place = 1
        self.current_angle = Bud.norm_angle(self.angle * self.current_ring + self.start_angle)
        self.current_height += self.ring_height

    def _next_pos(self) -> Tuple[Sphere, List[Sphere]]:
        """Return the parameters of the next bud to be positioned."""
        if self.current_ring_place < self.buds_per_ring:
            self.current_angle -= self.angle_step
            self.current_ring_place += 1
        else:
            self._next_ring()

        return Sphere(self.current_angle, self.current_height, self.ring_radius, self.bud_radius), None


class ChangingRingPositioner(RingPositioner):

    def __init__(self, angle, per_ring, scale, scale_radius=False, **kwargs):
        """Initialise the positioner.

        :param double angle: the angle by which each ring should be rotated relative to the previous one
        :param int per_ring: how many buds per ring
        :param double scale: by how much the buds of each ring should be smaller than the previous (percentage)
        :param bool scale_radius: whether to scale the radius, too
        """
        super().__init__(angle, per_ring, **kwargs)
        self.scale = scale / 100.0
        self.base_bud_radius = self.bud_radius
        self.scale_radius = scale_radius

    def reset(self):
        """Reset the positioner."""
        super().reset()
        self.bud_radius = self.base_bud_radius

    def _next_ring(self):
        """Move to the next ring, decreasing the size of the buds."""
        self.bud_radius -= self.scale * self.bud_radius
        super()._next_ring()

    @property
    def ring_radius(self):
        """Return the radius of each ring."""
        if self.scale_radius:
            return self.BASE_RADIUS - self.current_ring * self.delta * math.pi
        return self.BASE_RADIUS


class LowestAvailablePositioner(Positioner):

    def __init__(self, start_size, front=None, delta=0, random=0, **kwargs):
        self.start_size = start_size
        self.circles = front or []
        self.random = random
        self.delta = delta
        start_height = kwargs.pop('start_height', 0.0) / self.BASE_RADIUS
        super().__init__(size=self.BASE_RADIUS/start_size, start_height=start_height, **kwargs)

    def reset(self):
        """Reset the positioner."""
        super().reset()
        self.circles = []

    def next_radius(self):
        """Work out what the radius of the next bud should be and return it."""
        base = self.bud_radius

        scale = self.delta
        if self.random:
            scale += scale * random.randint(-self.random, self.random) / 100.0

        base -= scale * base

        self.bud_radius = base
        return base / self.BASE_RADIUS

    def lowest_on_front(self, checked_front, radius):
        potentials = filter(None, [
            closest_circle(prev, checked, radius)
            for checked, prev in zip(
                    checked_front + checked_front + checked_front,
                    cycle_ring(checked_front, 1) + cycle_ring(checked_front, 2) + cycle_ring(checked_front, 3)
            )
        ])
        # filter out all potentials that overlap with existing buds. Don't just check the front, coz the potentials
        # might lie lower than it. It should suffice to only check the last n buds, where n is twice the size of
        # the current front. Any lower buds will most likely be covered by the current front.
        potentials = [
            potential for potential in potentials
            if not check_collisions(potential, self.circles[-len(checked_front) * 2:])
        ]
        if not potentials:
            return None
        elif len(potentials) == 1:
            return potentials[0]
        return min(*potentials, key=lambda c: c.height)

    @property
    def current_front(self):
        """Get the current bud front (check the `front()` function for details)."""
        return front(self.circles)

    def _next_pos(self) -> Tuple[Sphere, List[Sphere]]:
        """
        Get the position of the next item.

        This can be calculated according to various algorithms and based
        on the current state of the meristem.

        :rtype: tuple
        :returns: a tuple with the (angle, height, radius, scale) of the next bud
        """
        current_front = self.current_front
        radius = self.next_radius()

        # first check if this is the first or second bud - if so, just insert them
        if len(self.circles) < 2:
            lowest = Sphere(
                Bud.norm_angle(self.current_angle + math.pi), self.current_height, scale=radius)

        # if the newest bud is on ground level then stick the bud in the first hole on ground level. This split
        # is to allow the next function to always assume that it gets touching buds. This makes things a lot easier.
        elif self.circles[-1].height == 0 and first_gap(self.circles, radius):
            lowest = Sphere(*first_gap(self.circles, radius), scale=radius)

        # if the first layer has been filled as much as possible, make the second layer by inserting buds in the holes
        # between the buds on the first layer
        elif current_front is None:
            lowest = self.lowest_on_front(sorted(self.circles, key=lambda c: c.angle), radius)
        # the new bud is a normal one, after the second layer of buds - proceed to the normal
        # first empty space algorithm, assuming that there are no gaps and using fronts
        else:
            lowest = self.lowest_on_front(current_front, radius)
        self.current_angle, self.current_height = lowest.angle, lowest.height
        self.circles.append(lowest)

        # the angle will always be between 0 and 2π, but the height will depend on the radius if the bud is to be
        # circular. This positioner uses normal coords (all buds are assumed to have a scale of 1), so the height
        # has to be scaled before it can be returned
        height = self.current_height * self.BASE_RADIUS

        return Sphere(self.current_angle, height, self.BASE_RADIUS, self.bud_radius), current_front
