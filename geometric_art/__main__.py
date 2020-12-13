import argparse
import os
import shutil
import time

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .geometric_art import CirclePopulation, CircleRenderer
from .geometric_art import PolygonPopulation, PolygonRenderer
from .geometric_art import compute_similarity, get_time_elapsed


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
