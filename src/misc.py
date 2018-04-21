
__author__ = "Felix Simkovic"
__date__ = "16 Apr 2018"
__version__ = "0.1"

from skimage import color
from skimage.draw import circle_perimeter
from skimage.feature import canny
from skimage.io import imread
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.util import img_as_ubyte

import matplotlib.pyplot as plt
import numpy as np


def determine_droplet_sizes_in_frame(frame, debug=False):
    if debug:
        imshow(frame)

    grayscale = color.rgb2gray(frame)
    if debug:
        imshow(grayscale)

    box = [650, 450, 50, 150]  # x, y, width, height
    subframe = grayscale[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
    if debug:
        imshow(subframe)

    edges = canny(subframe, sigma=3)
    if debug:
        imshow(edges)

    hough_radii = np.arange(8, 16, 1)
    hough_res = hough_circle(edges, hough_radii)
    _, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)

    for center_x, center_y, radius in zip(cx, cy, radii):
        circy, circx = circle_perimeter(center_y, center_x, radius)
        frame[circy + box[1], circx + box[0]] = (220, 20, 20)
    
    if debug:
        imshow(frame)

    return radii, frame


def imshow(frame, cmap=plt.cm.gray):
    fig, ax = plt.subplots()
    ax.imshow(frame, cmap=cmap)
    plt.show()


def hist(radii_per_video_per_frame, fname="test.png"):
    bins = np.arange(np.min(radii_per_video_per_frame), np.max(radii_per_video_per_frame)+1)
    fig, ax = plt.subplots()
    ax.hist(radii_per_video_per_frame, bins=bins)
    fig.savefig(fname, dpi=600)
