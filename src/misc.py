__author__ = "Felix Simkovic"
__date__ = "16 Apr 2018"
__version__ = "0.1"

from skimage import color
from skimage.draw import circle_perimeter
from skimage.feature import canny
from skimage.io import imread
from skimage.transform import hough_circle, hough_circle_peaks, hough_line, hough_line_peaks
from skimage.util import img_as_ubyte

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def determine_droplet_sizes_in_frame(frame, debug=False):
    if debug:
        imshow(frame)

    grayscale = color.rgb2gray(frame)
    if debug:
        imshow(grayscale)

    box = [450, 450, 1000, 150]  # x, y, width, height
    subframe = grayscale[box[1]:box[1] + box[3], box[0]:box[0] + box[2]]
    if debug:
        imshow(subframe)

    edges = canny(subframe, sigma=3)
    if debug:
        imshow(edges)

    hough_radii = np.arange(8, 14, 1)
    hough_res = hough_circle(edges, hough_radii)
    _, cx, cy, radii = hough_circle_peaks(
        hough_res, hough_radii, total_num_peaks=10)
    cx, cy, radii = cx[::1], cy[::1], radii[::1]

    cx_, cy_, radii_ = [cx[0]], [cy[0]], [radii[0]]
    for i in range(1, len(cx)):
        keeper = True

        for x, y, r in zip(cx_, cy_, radii_):
            thres = r if r > radii[i] else radii[i]
            if abs(cx[i] - x) <= thres and abs(cy[i] - y) <= thres:
                keeper = False
                break
    #
    #      if subframe[cy[i], cx[i]] > 0.4:
    #          keeper = False
    #
    #      if cx[i] < 50 or cy[i] < 50 or cy[i] > box[3] - 50:
    #          keeper = False

        if keeper:
            cx_.append(cx[i])
            cy_.append(cy[i])
            radii_.append(radii[i])

    measured = np.zeros(edges.shape)
    for center_x, center_y, radius in zip(cx_, cy_, radii_):
        circy, circx = circle_perimeter(center_y, center_x, radius)
        try:
            frame[circy + box[1], circx + box[0]] = (220, 20, 20)
            measured[circy, circx] = 1
        except:
            pass

    if debug:
        imshow(frame)

    #--- This code was used to establish estimates for the correction factors ---#
    #  hspace, angles, dists = hough_line(edges)
    #  x = np.arange(subframe.shape[1])
    #  points = []
    #  for _, angle, dist in zip(*hough_line_peaks(hspace, angles, dists, num_peaks=2)):
    #      y_bound = [(dist - 0 * np.cos(angle)) / np.sin(angle),
    #                 (dist - subframe.shape[1] * np.cos(angle)) / np.sin(angle)]
    #      y = np.floor((y_bound[1] - y_bound[0]) / (x[-1] - x[0]) * x + y_bound[0]).astype(int)
    #      frame[y + box[1], x + box[0]] = (220, 20, 20)
    #      measured[y - 1, x - 1] = 1
    #      points.append([[x[0], y[0]], [x[-1], y[-1]]])
    #  points = np.asarray(points)
    #  dist = np.mean(np.sqrt(np.sum((points[1] - points[0])**2, axis=1)))
    #  dist_factor = dist / 250.
    #  print(dist_factor)
    #
    #  if debug:
    #      imshow(measured)

    return radii, frame


def imshow(frame, cmap=plt.cm.gray):
    fig, ax = plt.subplots()
    ax.imshow(frame, cmap=cmap)
    plt.show()


def minmax(numbers):
    min_, max_ = 10 ^ 6, 0
    for array in numbers:
        for n in array:
            if n < min_:
                min_ = n
            if n > max_:
                max_ = n
    return min_, max_


def hist(radii_per_video_per_frame, fname='output.png', bin_=0.5):
    min_, max_ = minmax(radii_per_video_per_frame)
    labels = [
        "%d-microlitre" % (i + 1)
        for i in range(len(radii_per_video_per_frame))
    ]
    fig, ax = plt.subplots()
    ax.hist(
        radii_per_video_per_frame,
        bins=np.arange(min_, max_ + 1, bin_),
        label=labels)
    ax.legend()
    ax.set_xlabel(r"Droplet radius ($\mu$m)")
    ax.set_ylabel("Count")
    fig.savefig(fname, dpi=600)


def csv(radii_per_video_per_frame, fname='output.csv'):
    maxl = 0
    for r in radii_per_video_per_frame:
        if len(r) > maxl:
            maxl = len(r)

    data_ = np.full((len(radii_per_video_per_frame), maxl), np.nan)
    for i, r in enumerate(radii_per_video_per_frame):
        for j, e in enumerate(r):
            data_[i, j] = e

    header = ['Video %d' % (d + 1) for d in range(data_.shape[0])]
    pd.DataFrame(data_.T, columns=header).to_csv(fname, index=False)
