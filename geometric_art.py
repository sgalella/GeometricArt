import numpy as np
import os
import shutil
from PIL import Image, ImageDraw, ImageChops


def create_population(num_individuals, img_size, num_vertex):
    population = np.zeros((num_individuals, 2 * num_vertex + 4))
    population[:, :2 * num_vertex] = np.random.randint(img_size, size=population[:, :2 * num_vertex].shape)
    population[:, 2 * num_vertex:] = np.random.randint(256, size=population[:, 2 * num_vertex:].shape)
    return population


def render_image(population, img_size, num_vertex):
    canvas = Image.new('RGB', (img_size, img_size), color=(255, 255, 255))
    for individual in population:
        draw = ImageDraw.Draw(canvas, 'RGBA')
        points = list(individual[:2 * num_vertex].astype(int))
        color = tuple(individual[2 * num_vertex:].astype(int))
        draw.polygon(points, color)
    return canvas


def change_individual(individual, img_size, num_vertex):
    random_pos = np.random.randint(len(individual))
    if random_pos < 2 * num_vertex:
        individual[random_pos] = np.random.randint(img_size)
    else:
        individual[random_pos] = np.random.randint(256)
    return individual


def change_population(population, img_size, num_vertex):
    new_population = population.copy()
    random_individual = np.random.randint(population.shape[0])
    new_population[random_individual] = change_individual(new_population[random_individual], img_size, num_vertex)
    return new_population


def compute_similarity(target, output, max_difference):
    difference = np.sum(ImageChops.difference(target, output))
    similarity = 100 * (1 - (difference / max_difference))
    return similarity


def main(params, path):

    # Unpack parameters
    num_individuals = params['num_individuals']
    num_vertex = params['num_vertex']
    img_size = params['img_size']
    filename_path = params['filename_path']
    filename = filename_path.split('/')[-1]

    # Load target
    target = Image.open(filename_path).convert('RGB')
    target.save(f'{path}/run/target.png')

    # Initial image
    max_difference = np.prod(np.array(target).shape) * 255
    population = create_population(num_individuals, img_size, num_vertex)
    image = render_image(population, img_size, num_vertex)
    similarity = compute_similarity(target, image, max_difference)

    # Main loop
    iteration = 0
    changes = 0
    max_iteration = 300000
    print_iteration = 10000  # Print stats and store temporal image each print_interations

    while iteration < max_iteration:
        new_population = change_population(population, img_size, num_vertex)
        new_image = render_image(new_population, img_size, num_vertex)
        new_similarity = compute_similarity(target, new_image, max_difference)
        if new_similarity > similarity:
            similarity = new_similarity
            population = new_population
            image = new_image
            changes += 1
        if iteration % print_iteration == 0:
            image.save(f'{path}/run/output_{iteration}.png')
            print(f"Iteration: {iteration}  Changes: {changes}  Similarity: {similarity:.02f}%")
        iteration += 1

    image.save(f'{path}/run/output_{iteration}.png')
    print(f"Iteration: {iteration}  Similarity: {similarity:.02f}%")
    image.save(f'{path}/output/{similarity:.02f}_{num_individuals}_{num_vertex}_{filename}')


if __name__ == "__main__":
    # Random seed for reproducibility
    np.random.seed(1234)

    # Directory path
    path = None

    # Parameters
    params = {
        'num_individuals': 100,
        'num_vertex': 6,
        'img_size': 256,
        'filename_path': None
    }

    # Create folders to store temporal and generated images
    if os.path.isdir(f'{path}/run'):
        shutil.rmtree('run')
    if not os.path.isdir(f'{path}/output'):
        os.mkdir(f'{path}/output')
    os.mkdir(f'{path}/run')
    main(params, path)
