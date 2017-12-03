import math
from magnolia.meristem import Bud
from magnolia.graph import BudGraph


class Positioner(BudGraph):

    BASE_RADIUS = 3.0

    def __init__(self, colour=(0, 0, 0.7), start_height=0, start_angle=0, size=None):
        """Initialise the positioner."""
        super().__init__()
        self.colour = colour
        self.bud_radius = size if size else self.BASE_RADIUS
        self.start_height = self.current_height = start_height + self.bud_radius
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
        self.angle = angle
        self.angle_step = 2 * math.pi / per_ring
        self.current_ring_place = self.current_ring = 0
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

        return self.current_angle, self.current_height, self.BASE_RADIUS, self.bud_radius


class ChangingRingPositioner(RingPositioner):

    def __init__(self, angle, per_ring, delta, **kwargs):
        """Initialise the positioner.

        :param double angle: the angle by which each ring should be rotated relative to the previous one
        :param int per_ring: how many buds per ring
        :param double delta: by how much the buds of each ring should be smaller than the previous
        """
        super().__init__(angle, per_ring, **kwargs)
        self.delta = delta
        self.base_bud_radius = self.bud_radius

    def reset(self):
        """Reset the positioner."""
        super().reset()
        self.bud_radius = self.base_bud_radius

    def _next_ring(self):
        """Move to the next ring, decreasing the size of the buds."""
        self.bud_radius -= self.delta
        super()._next_ring()
