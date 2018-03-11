import math
from magnolia.meristem import Bud
from magnolia.graph import BudGraph
from magnolia.math.geometry import closest_circle, first_gap, front


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

    def _next_pos(self):
        """
        Get the position of the next item.

        This can be calculated according to various algorithms and based
        on the current state of the meristem.

        :rtype: tuple
        :returns: a tuple with the (angle, height, radius, scale) of the next bud
        """
        return 0, 1, self.bud_radius, 1

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

    def _next_pos(self):
        """Calculate the position of the next bud."""
        self.current_angle += self.lat_step

        if self.current_angle > math.pi * 2:
            self._current_row += 1
            self.current_angle = (self._current_row * self.angle_step) % self.lat_step
            self.current_height += self.ver_step

        return self.current_angle, self.current_height, self.BASE_RADIUS, self.bud_radius


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

        lat = abs(self.angle % self.angle_step)
        if lat > self.angle_step / 2:
            lat = self.angle_step - lat
        lat *= self.BASE_RADIUS
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

    def _next_pos(self):
        """Return the parameters of the next bud to be positioned."""
        if self.current_ring_place < self.buds_per_ring:
            self.current_angle -= self.angle_step
            self.current_ring_place += 1
        else:
            self._next_ring()

        return self.current_angle, self.current_height, self.ring_radius, self.bud_radius


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

    def __init__(self, start_size, front=None, **kwargs):
        self.start_size = start_size
        self.circles = front or []
        super().__init__(size=self.BASE_RADIUS/start_size, **kwargs)

    def reset(self):
        """Reset the positioner."""
        super().reset()
        self.circles = []

    def lowest_on_front(self, checked_front):
        lastx, lasty, lastr = checked_front[-1]
        first = [lastx + 2 * math.pi, lasty, lastr]
        offsetted_front = [first] + checked_front

        potenials = [
            closest_circle(prev, checked, self.bud_radius/self.BASE_RADIUS)
            for checked, prev in zip(checked_front, offsetted_front)
        ]
        return min(*potenials,  key=lambda c: c[1])

    def _next_pos(self):
        """
        Get the position of the next item.

        This can be calculated according to various algorithms and based
        on the current state of the meristem.

        :rtype: tuple
        :returns: a tuple with the (angle, height, radius, scale) of the next bud
        """
        current_front = front(self.circles)

        # first check if this is the first or second bud - if so, just insert them
        if len(self.circles) < 2:
            self.current_angle = Bud.norm_angle(self.current_angle + math.pi)

        # if the newest bud is on ground level then stick the bud in the first hole on ground level. This split
        # is to allow the next function to always assume that it gets touching buds. This makes things a lot easier.
        elif self.circles[-1][1] == 0 and first_gap(self.circles, self.bud_radius/self.BASE_RADIUS):
            self.current_angle, self.current_height = first_gap(self.circles, self.bud_radius/self.BASE_RADIUS)

        # if the first layer has been filled as much as possible, make the second layer by inserting buds in the holes
        # between the buds on the first layer
        elif current_front is None:
            self.current_angle, self.current_height = self.lowest_on_front(
                sorted(self.circles, key=lambda c: c[0], reverse=True))
        # the new bud is a normal one, after the second layer of buds - proceed to the normal
        # first empty space algorithm, assuming that there are no gaps and using fronts
        else:
            self.current_angle, self.current_height = self.lowest_on_front(current_front)

        self.circles.append((self.current_angle, self.current_height, self.bud_radius/self.BASE_RADIUS))
        return self.current_angle, self.current_height * self.BASE_RADIUS, self.BASE_RADIUS, self.bud_radius
