import time
from abc import ABC, abstractmethod

import numpy as np
from PIL import Image, ImageDraw, ImageChops


class ShapePopulation(ABC):
    """ Population of shapes. """
    @abstractmethod
    def _create(self):
        """ Creates the initial population. """
        pass

    @abstractmethod
    def change(self):
        """ Changes one individual in the population. """
        pass


class Renderer(ABC):
    """ Renders a population to obtain an image representation. """
    @abstractmethod
    def render(self, shape_population):
        """ Renders population. """
        pass


class PolygonPopulation(ShapePopulation):
    """ Population formed by polygons with different side lengths. """
    def __init__(self, num_individuals, size, num_sides):
        """
        Initializes the variables for the population of polygons.

        Args:
            num_individuals (int): Fixed number of individuals in the population.
            size (tuple): Target image dimensions.
            num_sides (int): Number of sides of the polygons.
        """
        self.num_individuals = num_individuals
        self.size = size
        self.num_sides = num_sides
        self.individuals = self._create()

    def _create(self):
        """
        Creates the initial population of polygons.

        Returns:
            individuals (np.array): Array of individuals.
        """
        individuals = np.zeros((self.num_individuals, 2 * self.num_sides + 4))
        individuals[:, ::2] = np.random.randint(self.size[0], size=individuals[:, ::2].shape)
        individuals[:, 1::2] = np.random.randint(self.size[1], size=individuals[:, 1::2].shape)
        individuals[:, 2 * self.num_sides:] = np.random.randint(256, size=individuals[:, 2 * self.num_sides:].shape)
        return individuals

    def change(self):
        """
        Changes one individual in one position.

        Returns:
            new_individuals: Population with an individual changed.
        """
        new_individuals = self.individuals.copy()
        random_individual = np.random.randint(self.individuals.shape[0])
        random_pos = np.random.randint(self.individuals.shape[1])
        if random_pos < 2 * self.num_sides:
            if random_pos % 2 == 0:
                new_individuals[random_individual][random_pos] = np.random.randint(self.size[0])
            else:
                new_individuals[random_individual][random_pos] = np.random.randint(self.size[1])
        else:
            new_individuals[random_individual][random_pos] = np.random.randint(256)
        return new_individuals


class CirclePopulation(ShapePopulation):
    """ Population formed by circles with different radius. """
    def __init__(self, num_individuals, size, max_radius):
        """
        Initializes the variables for the population of circles.

        Args:
            num_individuals (int): Fixed number of individuals in the population.
            size (tuple): Target image dimensions.
            max_radius (int): Maximum radius length of a circle.
        """
        self.num_individuals = num_individuals
        self.size = size
        self.max_radius = max_radius
        self.individuals = self._create()

    def _create(self):
        """
        Creates the initial population of polygons.

        Returns:
            individuals (np.array): Array of individuals.
        """
        individuals = np.zeros((self.num_individuals, 7))
        individuals[:, 0] = np.random.randint(self.size[0], size=individuals[:, 0].shape)
        individuals[:, 1] = np.random.randint(self.size[1], size=individuals[:, 1].shape)
        individuals[:, 2] = np.random.randint(self.max_radius, size=individuals[:, 2].shape)
        individuals[:, 3:7] = np.random.randint(256, size=individuals[:, 3:7].shape)
        return individuals

    def change(self):
        """
        Changes one individual in one position.

        Returns:
            new_individuals: Population with an individual changed.
        """
        new_individuals = self.individuals.copy()
        random_individual = np.random.randint(self.individuals.shape[0])
        random_pos = np.random.randint(self.individuals.shape[1])
        if random_pos == 0:
            new_individuals[random_individual][random_pos] = np.random.randint(self.size[0])
        elif random_pos == 1:
            new_individuals[random_individual][random_pos] = np.random.randint(self.size[1])
        elif random_pos == 2:
            new_individuals[random_individual][random_pos] = np.random.randint(self.max_radius)
        else:
            new_individuals[random_individual][random_pos] = np.random.randint(256)
        return new_individuals


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
