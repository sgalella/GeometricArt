import argparse
import os
import shutil
import time
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
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


def main(params):
    """ Runs the algorithm. """
    # Unpack parameters
    is_circle = params['is_circle']
    num_individuals = params['num_individuals']
    num_sides = params['num_sides']
    num_iterations = params['num_iterations']
    max_radius = params['max_radius']
    image = params['image']
    verbose = params['verbose']
    plot = params['plot']
    directory = params['directory']

    # Load target
    target_name = image.split('/')[-1]
    target = Image.open(image).convert('RGB')
    target.save(f'{directory}/run/target.png')
    size = target.size

    # Define functions according to shape
    if is_circle:
        shape_population = CirclePopulation(num_individuals, size, max_radius)
        renderer = CircleRenderer(size)
    else:
        shape_population = PolygonPopulation(num_individuals, size, num_sides)
        renderer = PolygonRenderer(size)

    # Initial image
    max_difference = np.prod(np.array(target).shape) * 255
    image = renderer.render(shape_population.individuals)
    similarity = compute_similarity(target, image, max_difference)

    # Main loop
    iteration = 0
    changes = 0
    print_iteration = 10000
    plot_iteration = 100

    if plot:
        # plt.ion()
        fig = plt.figure(figsize=(6, 3))
        ax1 = fig.add_subplot(121)
        ax1.imshow(target)
        plt.axis('off')
        ax2 = fig.add_subplot(122)
        updated_image = ax2.imshow(image)
        plt.axis('off')
        fig.subplots_adjust(wspace=0, hspace=0)
        plt.suptitle(f"Iterations: {iteration}  Changes: {changes}  Similarity: {similarity:.02f}%")
        text = plt.text(0, 285, f'Time: 10:00:00', fontsize=12, horizontalalignment='center')
        start = time.time()

    while iteration <= num_iterations:
        new_individuals = shape_population.change()
        new_image = renderer.render(new_individuals)
        new_similarity = compute_similarity(target, new_image, max_difference)
        if new_similarity > similarity:
            similarity = new_similarity
            shape_population.individuals = new_individuals
            image = new_image
            changes += 1
        if iteration % print_iteration == 0 and verbose:
            image.save(f'{directory}/run/output_{iteration}.png')
            print(f"Iterations: {iteration}  Changes: {changes}  Similarity: {similarity:.02f}%")
        if iteration % plot_iteration == 0 and plot:
            updated_image.set_data(image)
            plt.suptitle(f"Iterations: {iteration}  Changes: {changes}  Similarity: {similarity:.02f}%")
            hours, minutes, seconds = get_time_elapsed(start)
            text.set_text(f'Time: {hours:02d}:{minutes:02d}:{seconds:02d}')
            plt.draw()
            plt.pause(0.00001)
        iteration += 1
    plt.show()
    image.save(f'{directory}/output/{similarity:.02f}_{num_individuals}_{num_sides}_{target_name}')


if __name__ == "__main__":
    # Get arguments
    parser = argparse.ArgumentParser(description="Hill-climbing optimization to represent images using geometric shapes.")
    parser.add_argument("image", help="Path to the image to represent")
    parser.add_argument("-c", "--circle", help="Uses circles instead of polygons", action="store_true")
    parser.add_argument("-i", "--iterations", help="Number of iterations", type=int, default=100000)
    parser.add_argument("-m", "--maxradius", help="Specifies the maximum radius of circles", type=int, default=30)
    parser.add_argument("-n", "--number", help="Number of geometric shapes", type=int, default=50)
    parser.add_argument("-p", "--plot", help="Plots best image until current generation", action="store_true")
    parser.add_argument("-r", "--random", help="Random seed for the number generation", type=int)
    parser.add_argument("-s", "--sides", help="Number of sides for the polygons", type=int, default=6)
    parser.add_argument("-v", "--verbose", help="Prints current iteration, number of changes and similarity", action="store_true")
    args = parser.parse_args()

    # Random seed for reproducibility
    if args.random:
        np.random.seed(args.random)

    # Directory path
    path = os.getcwd()

    # Parameters
    params = {
        'is_circle': args.circle,
        'num_individuals': args.number,
        'num_sides': args.sides,
        'num_iterations': args.iterations,
        'max_radius': args.maxradius,
        'image': args.image,
        'verbose': args.verbose,
        'plot': args.plot,
        'directory': path,
    }

    # Create folders to store temporal and generated images
    if os.path.isdir(f'{path}/run'):
        shutil.rmtree('run')
    if not os.path.isdir(f'{path}/output'):
        os.mkdir(f'{path}/output')
    os.mkdir(f'{path}/run')

    main(params)
