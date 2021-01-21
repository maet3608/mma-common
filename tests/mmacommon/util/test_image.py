"""
.. module:: imageio
   :synopsis: Unit tests for imageio module
"""

import numpy as np
import pytest

from mmacommon.util.image import largest_component_mask, extract_contours


def test_largest_component_mask():
    image = np.array([[1, 0, 0],
                      [0, 0, 1],
                      [0, 1, 1]])
    mask = largest_component_mask(image)
    assert np.array_equal(mask, [[False, False, False],
                                 [False, False, True],
                                 [False, True, True]])


def test_largest_component_empty_mask():
    with pytest.raises(ValueError) as ex:
        image = np.zeros((3, 3))
        largest_component_mask(image)
    assert 'Input mask is empty!' in str(ex.value)


def test_extract_contours_empty_image():
    image = np.zeros((500, 500), np.float32)  # Empty image.
    contours = list(extract_contours(image, tolerance=2.0))
    assert len(contours) == 0


def test_extract_contours():
    image = np.zeros((500, 500), np.float32)  # Empty image.
    image[100:200, 100:200] = 1  # Add large filled square.
    image[300:320, 300:320] = 1  # Add small filled square.

    # Retrieve contour polygons.
    contours = list(extract_contours(image, tolerance=2.0))
    assert len(contours) == 2

    # Expected polygons for large and small square.
    big_sqr = [[200, 200, ], [100, 200], [100, 100], [200, 100], [200, 200]]
    small_sqr = [[320, 320], [300, 320], [300, 300], [320, 300], [320, 320]]

    # Compare polygons with one pixel absolute tolerance.
    assert np.allclose(contours[0], big_sqr, atol=1, rtol=0)
    assert np.allclose(contours[1], small_sqr, atol=1, rtol=0)
