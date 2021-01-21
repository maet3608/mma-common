"""
.. module:: imageio
   :synopsis: Unit tests for imageio
"""

import os
import pytest

import numpy as np
import numpy.testing as nt
import mmacommon.util.imageio as mio


def test_base64encode():
    data = b"test"
    b64 = mio.base64encode(data)
    assert b64 == 'dGVzdA=='


def test_base64decode():
    data = b"test"
    b64 = mio.base64encode(data)
    assert mio.base64decode(b64) == data


def test_save_and_load_raw_image():
    test_file_path = 'tests/data/test.jpg'
    try:
        img1 = mio.load_raw_image('tests/data/image_small.jpg')
        mio.save_raw_image(img1, test_file_path)
        img2 = mio.load_raw_image(test_file_path)
    except:
        raise
    finally:
        os.remove(test_file_path)
    assert img1 == img2


def test_is_image():
    arr = np.ones((4, 4, 3), dtype='uint8')
    assert mio.is_image(arr)
    arr = np.ones((4, 4, 3), dtype='uint8')
    assert mio.is_image(arr)
    arr = np.ones((4, 4, 3), dtype=float)
    assert not mio.is_image(arr)
    arr = np.ones((3, 3, 4), dtype='uint8')
    assert not mio.is_image(arr)


def test_image_from_url():
    base = os.getcwd().replace('\\', '/')
    url = 'file:///' + base + '/tests/data/image_small.jpg'
    image = mio.image_from_url(url)
    assert image.height == 130
    assert image.width == 130


def test_image_from_data_url():
    data_url = open('tests/data/image_small.dataurl').read()
    image = mio.image_from_data_url(data_url)
    assert image.height == 130
    assert image.width == 130


def test_ndarray_from_url():
    base = os.getcwd().replace('\\', '/')
    expected = np.identity(4, dtype='uint8')

    url = 'file:///' + base + '/tests/data/ndarray.npy'
    mat = mio.ndarray_from_url(url)
    nt.assert_equal(mat, expected)

    url = 'file:///' + base + '/tests/data/ndarray.npz'
    mat = mio.ndarray_from_url(url)
    nt.assert_equal(mat, expected)

    url = 'file:///' + base + '/tests/data/image_small.png'
    expected = np.array(mio.image_from_url(url))
    nt.assert_equal(mio.ndarray_from_url(url), expected)


def test_ndarray_from_to_bytes():
    arr_in = np.ones((2, 3), dtype='uint8')
    bdata = mio.ndarray_to_bytes(arr_in)
    arr_out = mio.ndarray_from_bytes(bdata)
    nt.assert_equal(arr_out, arr_in)


def test_ndarray_to_data_url():
    mat = np.ones((1, 2), dtype='uint8')
    data_url = mio.ndarray_to_data_url(mat)
    assert data_url.startswith("data:image/png;base64,iVBORw0KGgoAAAANSUhE")
    assert data_url.endswith("AAAAASUVORK5CYII=")

    mat = np.ones((1, 2), dtype=float)
    data_url = mio.ndarray_to_data_url(mat)
    assert data_url.startswith("data:ndarray/npz;base64,k05VTVB")
    assert data_url.endswith("AAAAPA/")


def test_ndarray_from_data_url():
    data_url = open('tests/data/image_small.dataurl').read()
    mat = mio.ndarray_from_data_url(data_url)
    assert mat.shape == (130, 130, 3)

    mat = np.ones((1, 2), dtype=float)
    data_url = mio.ndarray_to_data_url(mat)
    nt.assert_equal(mio.ndarray_from_data_url(data_url), mat)


def test_imagefile_to_ndarray():
    path = 'tests/data/image_small.jpg'
    mat = mio.imagefile_to_ndarray(path)
    assert mat.shape == (130, 130, 3)


def test_ndarray_to_imagefile():
    path = 'tests/data/image_small.png'
    mat_out = mio.imagefile_to_ndarray(path)
    mio.ndarray_to_imagefile(mat_out, path)
    mat_in = mio.imagefile_to_ndarray(path)
    assert np.allclose(mat_out, mat_in)


def test_pil_to_data_url():
    data_url = open('tests/data/image_small.dataurl').read()
    pil_image = mio.image_from_data_url(data_url)
    for fmt in ['jpg', 'tif', 'png', 'gif', 'bmp']:
        mio.pil_to_data_url(pil_image, fmt)


def test_image_to_data_url():
    img = mio.load_raw_image('tests/data/image_small.jpg')
    data_url = open('tests/data/image_small.dataurl').read()
    assert mio.image_to_data_url(img, 'jpg') == data_url


def test_imagefile_to_data_url():
    expected_data_url = open('tests/data/image_small.dataurl').read()
    data_url = mio.imagefile_to_data_url('tests/data/image_small.jpg')
    print('expected_data_url:', expected_data_url[:60])
    print('data_url         :', data_url[:60])

    assert expected_data_url == data_url


def test_imagefile_to_data_url_types():
    data_url = mio.imagefile_to_data_url('tests/data/image_small.jpg')
    assert data_url.startswith('data:image/jpg')
    data_url = mio.imagefile_to_data_url('tests/data/image_small.gif')
    assert data_url.startswith('data:image/gif')
    data_url = mio.imagefile_to_data_url('tests/data/image_small.bmp')
    assert data_url.startswith('data:image/bmp')
    data_url = mio.imagefile_to_data_url('tests/data/image_small.png')
    assert data_url.startswith('data:image/png')
    data_url = mio.imagefile_to_data_url('tests/data/image_small.tif')
    assert data_url.startswith('data:image/tif')


def test_imagefile_unknown_type():
    with pytest.raises(ValueError) as ex:
        mio.imagefile_to_data_url('tests/data/image_small.dataurl')
    assert 'Unknown image type:' in str(ex.value)


def test_parse_data_url():
    base64data = '/9j/4SXNRXhpZgAUAFFABRQB//Z'
    data_url = 'data:image/jpg;base64,' + base64data
    datatype, subtype, encoding, data = mio.parse_data_url(data_url)
    assert datatype == 'image'
    assert subtype == 'jpg'
    assert encoding == 'base64'
    assert data == base64data


def test_parse_incorrect_data_url():
    with pytest.raises(ValueError) as ex:
        data_url = '/9j/4SXNRXhpZgAUAFFABRQB//Z'
        mio.parse_data_url(data_url)
    assert 'Not a data URL' in str(ex.value)

    with pytest.raises(ValueError) as ex:
        data_url = 'data:image,/9j/4SXNRXhpZgAUAFFABRQB//Z'
        mio.parse_data_url(data_url)
    assert 'Data URL not in correct format' in str(ex.value)


def test_extract_data_and_type():
    data_url = open('tests/data/image_small.dataurl').read()
    bdata = mio.load_raw_image('tests/data/image_small.jpg')
    data, datatype, subtype = mio.extract_data_and_type(data_url)
    assert data == bdata
    assert datatype == 'image'
    assert subtype == 'jpg'

    mat = np.ones((1, 2), dtype=float)
    bdata = mio.ndarray_to_bytes(mat)
    data_url = mio.ndarray_to_data_url(mat)
    data, datatype, subtype = mio.extract_data_and_type(data_url)
    assert data == bdata
    assert datatype == 'ndarray'
    assert subtype == 'npz'


def test_extract_data_and_type_no_base64():
    data_url = 'data:image/jpg;base32,/9j/4SXNRXhpZgAUAFFABRQB//Z'
    with pytest.raises(ValueError) as ex:
        mio.extract_data_and_type(data_url)
    assert 'Invalid data' in str(ex.value)
