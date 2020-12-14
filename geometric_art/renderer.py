from abc import ABC, abstractmethod

from PIL import Image, ImageDraw


class Renderer(ABC):
    """ Renders a population to obtain an image representation. """
    @abstractmethod
    def render(self, shape_population):
        """ Renders population. """
        pass


class CircleRenderer(Renderer):
    """ Renderer of a population of circles. """
    def __init__(self, size):
        """
        Initializes a renderer for circles.

        Args:
            size (tuple): Target image dimensions.
        """
        self.size = size

    def render(self, individuals):
        """
        Renders a population of circles.

        Args:
            individuals (np.array): Array of individuals.

        Returns:
            canvas (PIL.Image): Image representation of the population.
        """
        canvas = Image.new('RGB', self.size, color=(255, 255, 255))
        for individual in individuals:
            draw = ImageDraw.Draw(canvas, 'RGBA')
            x, y = tuple(individual[:2].astype(int))
            radius = individual[2].astype(int)
            color = tuple(individual[3:].astype(int))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), color)
        return canvas


class PolygonRenderer(Renderer):
    """ Renderer of a population of polygons """
    def __init__(self, size):
        """
        Initializes a renderer for polygons.

        Args:
            size (tuple): Target image dimensions.
        """
        self.size = size

    def render(self, individuals):
        """
        Renders a population of polygons.

        Args:
            individuals (np.array): Array of individuals.

        Returns:
            canvas (PIL.Image): Image representation of the population.
        """
        canvas = Image.new('RGB', self.size, color=(255, 255, 255))
        for individual in individuals:
            draw = ImageDraw.Draw(canvas, 'RGBA')
            points = list(individual[:-4].astype(int))
            color = tuple(individual[-4:].astype(int))
            draw.polygon(points, color)
        return canvas
