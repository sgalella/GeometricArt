from abc import ABC, abstractmethod

import numpy as np


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
