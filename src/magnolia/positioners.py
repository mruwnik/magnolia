from magnolia.meristem import Bud, Meristem


class Positioner(Meristem):

    BASE_RADIUS = 3.0
    colour = (0, 0, 0.7)

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
        return 0, 1, self.BASE_RADIUS, 1

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

    def recalculate(self, index=0):
        """Recalculate the positions of all items (starting from the provided index)."""
        for item in self.objects[index:]:
            angle, height, radius, scale = self._next_pos()
            item.angle = angle
            item.height = height
            item.radius = radius
            item.scale = scale
        self._vertices = self.concat('vertices', self.displayables)
