import random

import cv2
import numpy as np

from scripts.color.generate_color import generate_random_color
from scripts.common.flatten import flatten


def remove_corners_at_random(points):
    """
    Remove a random number of corners from a list of points.

    Parameters:
    points (list of tuple): A list of points (x, y).

    Returns:
    list of tuple: A list of points with some corners removed, maintaining the order.
    """
    indices_to_remove = random.sample([0, 3, 6, 9], random.randint(0, 4))
    remaining_points = []
    for i, point in enumerate(points):
        if i not in indices_to_remove:
            remaining_points.append(point)
    return remaining_points


def points_in_between(p1, p2, fraction1=1 / 5, fraction2=4 / 5):
    """
    Create two points between two given points at specified fractions.

    Parameters:
    p1 (tuple): The first point (x1, y1).
    p2 (tuple): The second point (x2, y2).
    fraction1 (float): The fraction of the distance from p1 for the first point.
    fraction2 (float): The fraction of the distance from p1 for the second point.

    Returns:
    list: Two points located at the specified fractions between p1 and p2.
    """
    x1, y1 = p1
    x2, y2 = p2
    point_f1 = (x1 + (x2 - x1) * fraction1, y1 + (y2 - y1) * fraction1)
    point_f2 = (x1 + (x2 - x1) * fraction2, y1 + (y2 - y1) * fraction2)
    return [point_f1, point_f2]


def rectangle_points_with_additional(x, y, width, height):
    """
    Generate points for a rectangle with additional points near the corners.

    Parameters:
    x (int): The x-coordinate of the top-left corner.
    y (int): The y-coordinate of the top-left corner.
    width (int): The width of the rectangle.
    height (int): The height of the rectangle.

    Returns:
    list of tuple: A list of points representing the corners and additional points.
    """
    top_left = (x, y)
    top_right = (x + width, y)
    bottom_right = (x + width, y + height)
    bottom_left = (x, y + height)

    separation_denominator = 2.2 + random.random() * 7
    separation_a = 1 / separation_denominator
    separation_b = (separation_denominator - 1) / separation_denominator

    points = flatten([
        top_left, points_in_between(top_left, top_right, separation_a, separation_b),
        top_right, points_in_between(top_right, bottom_right, separation_a, separation_b),
        bottom_right, points_in_between(bottom_right, bottom_left, separation_a, separation_b),
        bottom_left, points_in_between(bottom_left, top_left, separation_a, separation_b)
    ])

    return [(int(item[0]), int(item[1])) for item in points]


def provide_color(randomize=False):
    if randomize:
        return generate_random_color()
    return 255, 255, 255


def draw_polygon(image, points, color=(255, 0, 0), thickness=2):
    """
    Draw a polygon on an image using a list of points.

    Parameters:
    image (np.ndarray): The image on which to draw the polygon.
    points (list of tuple): A list of points (x, y) representing the corners of the polygon.
    color (tuple): The color of the polygon lines (default is red).
    thickness (int): The thickness of the polygon lines (default is 2).

    Returns:
    np.ndarray: The image with the polygon drawn on it.
    """
    num_points = len(points)
    for i in range(num_points):
        start_point = points[i]
        end_point = points[(i + 1) % num_points]
        if random.random() < .8:
            cv2.line(image, start_point, end_point, provide_color(), thickness, cv2.LINE_AA)
    return image


def draw_random_polygon(image, x, y, width, height, thickness=2):
    """
    Draw a random polygon on an image within a specified rectangle.

    Parameters:
    image (np.ndarray): The image on which to draw the polygon.
    x (int): The x-coordinate of the top-left corner of the rectangle.
    y (int): The y-coordinate of the top-left corner of the rectangle.
    width (int): The width of the rectangle.
    height (int): The height of the rectangle.
    thickness (int): The thickness of the polygon lines (default is 2).

    Returns:
    np.ndarray: The image with the random polygon drawn on it.
    """
    points = rectangle_points_with_additional(x, y, width, height)
    points = remove_corners_at_random(points)
    return draw_polygon(image, points, provide_color(), thickness)


def draw_polygon_matrix(n, m, image_width, image_height, thickness=2, padding=10):
    """
    Draw a matrix of random polygons on an image.

    Parameters:
    n (int): The number of rows of polygons.
    m (int): The number of columns of polygons.
    image_width (int): The width of the image.
    image_height (int): The height of the image.
    padding (int): The padding between polygons.

    Returns:
    np.ndarray: The image with the matrix of random polygons drawn on it.
    """
    image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    image_width -= padding
    image_height -= padding
    poly_width = image_width // m
    poly_height = image_height // n
    for i in range(n):
        for j in range(m):
            x = j * poly_width + padding // 2
            y = i * poly_height + padding // 2
            image = draw_random_polygon(image, x, y, poly_width, poly_height, thickness)
    return image


def draw_center_circle(image, n, m, image_width, image_height, thickness=2, padding=10):
    """
    Draw a circle in the middle of the image with a diameter matching the width of the polygons.

    Parameters:
    image (np.ndarray): The image on which to draw the circle.
    n (int): The number of rows of polygons.
    m (int): The number of columns of polygons.
    image_width (int): The width of the image.
    image_height (int): The height of the image.
    thickness (int): The thickness of the circle perimeter line.
    padding (int): The padding between polygons.

    Returns:
    np.ndarray: The image with the circle drawn on it.
    """
    poly_width = (image_width - padding) // m
    poly_height = (image_height - padding) // n
    center_x = image.shape[1] // 2
    center_y = image.shape[0] // 2

    radius = int(((poly_width + poly_height) / 2) // 2)
    radius += int(radius * (random.random() * .4 + .15))

    cv2.circle(image, (center_x, center_y), radius, (0, 0, 0), -1)
    cv2.circle(image, (center_x, center_y), radius, provide_color(), thickness, cv2.LINE_AA)
    return image


def generate_monochromatic_chip(n=None, m=None, image_width=800, image_height=None, padding_percentage=.03, draw_circle_probability=0.5):
    """
    Draw a random chip consisting of a matrix of random polygons and optionally a circle in the middle.

    Parameters:
    n (int): The number of rows of polygons. Default is a random integer between 2 and 4.
    m (int): The number of columns of polygons. Default is the same as n.
    image_width (int): The width of the image. Default is 800.
    image_height (int): The height of the image. Default is 800.
    padding (int): The padding between polygons. Default is 10.
    draw_circle_probability (float): The probability of drawing a circle in the middle. Default is 0.5.

    Returns:
    np.ndarray: The generated image with the random chip.
    """

    if image_height is None:
        image_height = int(image_width / (random.random() * 1.5 + .5))

    if n is None:
        n = random.randint(2, 4)

    if m is None:
        m = n

    padding = int(image_width * padding_percentage)
    thickness = int(image_width * .0035)

    # Draw the matrix of random polygons on the image
    image = draw_polygon_matrix(n, m, image_width, image_height, thickness, padding)

    # Randomly decide whether to draw the center circle based on the given probability
    if random.random() < draw_circle_probability:
        image = draw_center_circle(image, n, m, image_width, image_height, thickness, padding)

    if random.random() < draw_circle_probability:
        image = draw_center_circle(image, n, m, image_width, image_height, thickness, padding)

    ksize = (4, 4)
    image = cv2.blur(image, ksize)

    return image
