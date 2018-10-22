"""
.. module:: image
   :synopsis: Basic operations on images.
"""

import numpy as np
import skimage.measure as skm


def largest_component_mask(image):
    """
    Compute a boolean mask of the largest component within the input image.

    :param numpy.array(dtype=int) image: Binary image.
    :return: Mask for the largest component in the image.
    :rtype: numpy.array(dtype=bool)
    :raises: ValueError if input image is empty (all zeros or ones).
    """
    labelled_image, num = skm.label(image, return_num=True)
    if not num:
        raise ValueError('Input mask is empty!')
    regionprops = enumerate(skm.regionprops(labelled_image))
    max_label, _ = max(regionprops, key=lambda rp: rp[1].area)
    return labelled_image == max_label + 1


def extract_contours(image, tolerance=2.0):
    """
    Return contour polygons for all objects within the image.

    The methods extracts closed polygons for the contours of all white blobs
    within the binary input image and smoothens the contour polygons using the
    Douglas-Peucker algorithm. References:

    - https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
    - http://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.find_contours
    - http://scikit-image.org/docs/dev/auto_examples/edges/plot_polygon.html#example-edges-plot-polygon-py

    :param numpy.array(dtype=int) image: Binary image with 0..n objects.
    :param float tolerance: Smoothing of the polygon. 0 means no smoothing.
    :return: Closed polygons around contours of each image object.
    :rtype: Generator over (n,2)-ndarrays.

            Each contour is an ndarray of shape (n, 2),
            consisting of n (column, row) coordinates along the contour.
    """
    for contour in skm.find_contours(image, 0.5):
        yield np.fliplr(skm.approximate_polygon(contour, tolerance))
