import numpy as np
import os
import shutil
import argparse
import matplotlib.pyplot as plt
import time
from PIL import Image, ImageDraw, ImageChops


def create_population_polygons(num_individuals, size, num_sides):
    """
    Initializes the population of polygons in random positions.

    Args:
        num_individuals (int): Number of polygons in the canvas.
        size (int): Dimensions on the canvas.
        num_sides (int): Number of sides for all polygons.

    Returns:
        np.array: Array containing different individuals.
    """
    population = np.zeros((num_individuals, 2 * num_sides + 4))
    population[:, ::2] = np.random.randint(size[0], size=population[:, ::2].shape)
    population[:, 1::2] = np.random.randint(size[1], size=population[:, 1::2].shape)
    population[:, 2 * num_sides:] = np.random.randint(256, size=population[:, 2 * num_sides:].shape)
    return population


def render_image_polygons(population, size, num_sides):
    """
    Draws each polygon on the canvas.

    Args:
        population (np.array): Array containing different individuals.
        size (int): Dimensions on the canvas.
        num_sides (int): Number of sides for all polygons.

    Returns:
       Image : Canvas with polygons on it.
    """
    canvas = Image.new('RGB', size, color=(255, 255, 255))
    for individual in population:
        draw = ImageDraw.Draw(canvas, 'RGBA')
        points = list(individual[:2 * num_sides].astype(int))
        color = tuple(individual[2 * num_sides:].astype(int))
        draw.polygon(points, color)
    return canvas


def change_population_polygons(population, size, num_sides):
    """
    Changes an individual from the population.

    Args:
        population (np.array): Array containing different individuals.
        size (int): Dimensions on the canvas.
        num_sides (int): Number of sides for all polygons.

    Returns:
        np.array: Contains population with one individual changed randomly.
    """
    new_population = population.copy()
    random_individual = np.random.randint(population.shape[0])
    random_pos = np.random.randint(population.shape[1])
    if random_pos < 2 * num_sides:
        if random_pos % 2 == 0:
            new_population[random_individual][random_pos] = np.random.randint(size[0])
        else:
            new_population[random_individual][random_pos] = np.random.randint(size[1])
    else:
        new_population[random_individual][random_pos] = np.random.randint(256)
    return new_population


def create_population_circles(num_individuals, size, max_radius):
    """
    Initializes the population of  in random positions.

    Args:
        num_individuals (int): Number of polygons in the canvas.
        size (int): Dimensions on the canvas.
        max_radius (int): Maximum possible radius.

    Returns:
        np.array: Array containing different individuals.
    """
    population = np.zeros((num_individuals, 7))
    population[:, 0] = np.random.randint(size[0], size=population[:, 0].shape)
    population[:, 1] = np.random.randint(size[1], size=population[:, 1].shape)
    population[:, 2] = np.random.randint(max_radius, size=population[:, 2].shape)
    population[:, 3:7] = np.random.randint(256, size=population[:, 3:7].shape)
    return population


def render_image_circles(population, size, _max_radius):
    """
    Draws each circle on the canvas.

    Args:
        population (np.array): Array containing different individuals.
        size (int): Dimensions on the canvas.
        _max_radius (int): Maximum possible radius.

    Returns:
        Image: Canvas with circles on it.
    """
    canvas = Image.new('RGB', size, color=(255, 255, 255))
    for individual in population:
        draw = ImageDraw.Draw(canvas, 'RGBA')
        x, y = tuple(individual[:2].astype(int))
        radius = individual[2].astype(int)
        color = tuple(individual[3:].astype(int))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), color)
    return canvas


def change_population_circles(population, size, max_radius):
    """
    Changes an individual from the population.

    Args:
        population (np.array): Array containing different individuals.
        size (int): Dimensions on the canvas.
        max_radius (int): Maximum possible radius.

    Returns:
        np.array: Contains population with one individual changed randomly.
    """
    new_population = population.copy()
    random_individual = np.random.randint(population.shape[0])
    random_pos = np.random.randint(population.shape[1])
    if random_pos == 0:
        new_population[random_individual][random_pos] = np.random.randint(size[0])
    elif random_pos == 1:
        new_population[random_individual][random_pos] = np.random.randint(size[1])
    elif random_pos == 2:
        new_population[random_individual][random_pos] = np.random.randint(max_radius)
    else:
        new_population[random_individual][random_pos] = np.random.randint(256)
    return new_population


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
        create_population = create_population_circles
        render_image = render_image_circles
        change_population = change_population_circles
        geometry_params = (size, max_radius)
    else:
        create_population = create_population_polygons
        render_image = render_image_polygons
        change_population = change_population_polygons
        geometry_params = (size, num_sides)

    # Initial image
    max_difference = np.prod(np.array(target).shape) * 255
    population = create_population(num_individuals, *geometry_params)
    image = render_image(population, *geometry_params)
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
        new_population = change_population(population, *geometry_params)
        new_image = render_image(new_population, *geometry_params)
        new_similarity = compute_similarity(target, new_image, max_difference)
        if new_similarity > similarity:
            similarity = new_similarity
            population = new_population
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
