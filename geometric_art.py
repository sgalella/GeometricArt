import numpy as np
import os
import shutil
import argparse
from PIL import Image, ImageDraw, ImageChops


def create_population(num_individuals, size, num_sides):
    population = np.zeros((num_individuals, 2 * num_sides + 4))
    population[:, :2 * num_sides] = np.random.randint(size[0], size=population[:, :2 * num_sides].shape)
    population[:, 2 * num_sides:] = np.random.randint(256, size=population[:, 2 * num_sides:].shape)
    return population


def render_image(population, size, num_sides):
    canvas = Image.new('RGB', size, color=(255, 255, 255))
    for individual in population:
        draw = ImageDraw.Draw(canvas, 'RGBA')
        points = list(individual[:2 * num_sides].astype(int))
        color = tuple(individual[2 * num_sides:].astype(int))
        draw.polygon(points, color)
    return canvas


def change_individual(individual, size, num_sides):
    random_pos = np.random.randint(len(individual))
    if random_pos < 2 * num_sides:
        individual[random_pos] = np.random.randint(size[0])
    else:
        individual[random_pos] = np.random.randint(256)
    return individual


def change_population(population, size, num_sides):
    new_population = population.copy()
    random_individual = np.random.randint(population.shape[0])
    new_population[random_individual] = change_individual(new_population[random_individual], size, num_sides)
    return new_population


def compute_similarity(target, output, max_difference):
    difference = np.sum(ImageChops.difference(target, output))
    similarity = 100 * (1 - (difference / max_difference))
    return similarity


def main(params):

    # Unpack parameters
    num_individuals = params['num_individuals']
    num_sides = params['num_sides']
    num_iterations = params['num_iterations']
    image = params['image']
    verbose = params['verbose']
    directory = params['directory']

    # Load target
    target_name = image.split('/')[-1]
    target = Image.open(image).convert('RGB')
    target.save(f'{directory}/run/target.png')

    # Get image size
    size = target.size

    # Initial image
    max_difference = np.prod(np.array(target).shape) * 255
    population = create_population(num_individuals, size, num_sides)
    image = render_image(population, size, num_sides)
    similarity = compute_similarity(target, image, max_difference)

    # Main loop
    iteration = 0
    changes = 0
    print_iteration = num_iterations // 10  # Print stats and store temporal image each print_interations

    while iteration <= num_iterations:
        new_population = change_population(population, size, num_sides)
        new_image = render_image(new_population, size, num_sides)
        new_similarity = compute_similarity(target, new_image, max_difference)
        if new_similarity > similarity:
            similarity = new_similarity
            population = new_population
            image = new_image
            changes += 1
        if iteration % print_iteration == 0 and verbose:
            image.save(f'{directory}/run/output_{iteration}.png')
            print(f"Iteration: {iteration}  Changes: {changes}  Similarity: {similarity:.02f}%")
        iteration += 1

    image.save(f'{directory}/output/{similarity:.02f}_{num_individuals}_{num_sides}_{target_name}')


if __name__ == "__main__":

    # Get arguments
    parser = argparse.ArgumentParser(description="Hill-climbing optimization to represent images using geometric shapes.")
    parser.add_argument("image", help="Path to the image to represent")
    parser.add_argument("-r", "--random", help="Random seed for the number generation", type=int)
    parser.add_argument("-n", "--number", help="Number of geometric shapes", type=int, default=50)
    parser.add_argument("-s", "--sides", help="Number of sides for the polygon", type=int, default=6)
    parser.add_argument("-i", "--iterations", help="Number of iterations", type=int, default=100000)
    parser.add_argument("-v", "--verbose", help="Print information", action="store_true")
    args = parser.parse_args()

    # Random seed for reproducibility
    if args.random:
        np.random.seed(args.random)

    # Directory path
    path = os.getcwd()

    # Parameters
    params = {
        'num_individuals': args.number,
        'num_sides': args.sides,
        'num_iterations': args.iterations,
        'image': args.image,
        'verbose': args.verbose,
        'directory': path,
    }

    # Create folders to store temporal and generated images
    if os.path.isdir(f'{path}/run'):
        shutil.rmtree('run')
    if not os.path.isdir(f'{path}/output'):
        os.mkdir(f'{path}/output')
    os.mkdir(f'{path}/run')

    main(params)
