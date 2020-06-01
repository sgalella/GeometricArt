# Geometric Art
Hill-climbing optimization to represent images using geometric shapes. Based on the idea from [Roger Alsing's Genetic Programming: Evolution of Mona Lisa](https://rogerjohansson.blog/2008/12/07/genetic-programming-evolution-of-mona-lisa/) with some improvements from [AlteredQualia's Evolution of Mona Lisa in Javascript](https://alteredqualia.com/visualization/evolve/).

<p align="center">
    <img width="500" height="300" src="images/geometric_art.gif">
</p>



## Examples

Left original, right generated. All images were created using 300,000 iterations and 50 polygons. The number of sides was kept fixed at 6. Percentage above represents the similarity between the original and the generated. The similarity is computed as the absolute difference between each pixel. 

<p align="center">
    <img width="800" height="350" src="images/gallery.png">
</p>


## Installation

To install the dependencies, run the following command:

```bash
pip install -r requirements.txt
```



## Usage

Run the program as:

```bash
python geometric_art.py path-to-image
```

Additionally, you can change the parameters by adding the corresponding flag and value (if integer):

|        Flag        |                        Description                         | Default |
| :----------------: | :--------------------------------------------------------: | :-----: |
| _-i, --iterations_ |                    Number of iterations                    | 1000000 |
|   _-n, --number_   |                 Number of geometric shapes                 |   50    |
|    _-p, --plot_    |         Plots best image until current generation          |  False  |
|   _-r, --random_   |           Random seed for the number generation            |    –    |
|   _-s, --sides_    |              Number of sides for the polygons              |    6    |
|  _-v, --verbose_   | Prints current iteration, number of changes and similarity |  False  |

To see the flags on the command line, run:

```
python geometric_art.py --help
```

