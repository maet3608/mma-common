"""
.. module:: imageio
   :synopsis: Unit tests for imageio
"""

import os
import pytest

import numpy as np
import mmacommon.util.imageio as mio


def test_save_and_load_raw_image():
    test_file_path = 'tests/data/test.jpg'
    try:
        img1 = mio.load_raw_image('tests/data/fundus_image_small.jpg')
        mio.save_raw_image(img1, test_file_path)
        img2 = mio.load_raw_image(test_file_path)
    except:
        raise
    finally:
        os.remove(test_file_path)
    assert img1 == img2


def test_image_from_url():
    base = os.getcwd().replace('\\', '/')
    url = 'file:///' + base + '/tests/data/fundus_image_small.jpg'
    image = mio.image_from_url(url)
    assert image.height == 130
    assert image.width == 130


def test_image_from_data_url():
    data_url = open('tests/data/fundus_image_small.dataurl').read()
    image = mio.image_from_data_url(data_url)
    assert image.height == 130
    assert image.width == 130


def test_ndarray_to_data_url():
    mat = np.ones((1, 2), dtype='uint8')
    data_url = mio.ndarray_to_data_url(mat)
    assert data_url.startswith("data:image/png;base64,iVBORw0KGgoAAAANSUhE")
    assert data_url.endswith("AAAAASUVORK5CYII=")


def test_ndarray_from_data_url():
    data_url = open('tests/data/fundus_image_small.dataurl').read()
    mat = mio.ndarray_from_data_url(data_url)
    assert mat.shape == (130, 130, 3)


def test_ndvolume_to_data_url():
    mat = np.ones((3, 1, 2), dtype='uint8')
    data_url = mio.ndvolume_to_data_url(mat)
    assert type(data_url) is list
    assert len(data_url) == 3
    assert data_url[0].startswith("data:image/png;base64,iVBORw0KGgoAAAANSUhE")
    assert data_url[0].endswith("AAAAASUVORK5CYII=")


def test_ndvolume_from_data_url():
    with open('tests/data/fundus_volume_small.dataurl') as f:
        data_url = list(f)
    mat = mio.ndvolume_from_data_url(data_url)
    assert mat.shape == (3, 130, 130, 3)
    with pytest.raises(ValueError) as ex:
        data_url = 'data:image/png;base64,iVBORw0KGgoAAAANSUhE'
        mio.ndvolume_from_data_url(data_url)
    assert 'Expected array of data URLs' in str(ex)


def test_imagefile_to_ndarray():
    path = 'tests/data/fundus_image_small.jpg'
    mat = mio.imagefile_to_ndarray(path)
    assert mat.shape == (130, 130, 3)


def test_ndarray_to_imagefile():
    path = 'tests/data/fundus_image_small.png'
    mat_out = mio.imagefile_to_ndarray(path)
    mio.ndarray_to_imagefile(mat_out, path)
    mat_in = mio.imagefile_to_ndarray(path)
    assert np.allclose(mat_out, mat_in)


def test_pil_to_data_url():
    data_url = open('tests/data/fundus_image_small.dataurl').read()
    pil_image = mio.image_from_data_url(data_url)
    for fmt in ['jpg', 'tif', 'png', 'gif', 'bmp']:
        mio.pil_to_data_url(pil_image, fmt)


def test_image_to_data_url():
    img = mio.load_raw_image('tests/data/fundus_image_small.jpg')
    data_url = open('tests/data/fundus_image_small.dataurl').read()
    assert mio.image_to_data_url(img, 'jpg') == data_url


def test_imagefile_to_data_url():
    expected_data_url = open('tests/data/fundus_image_small.dataurl').read()
    data_url = mio.imagefile_to_data_url('tests/data/fundus_image_small.jpg')
    print('expected_data_url:', expected_data_url[:60])
    print('data_url         :', data_url[:60])

    assert expected_data_url == data_url


def test_imagefile_to_data_url_types():
    data_url = mio.imagefile_to_data_url('tests/data/fundus_image_small.jpg')
    assert data_url.startswith('data:image/jpg')
    data_url = mio.imagefile_to_data_url('tests/data/fundus_image_small.gif')
    assert data_url.startswith('data:image/gif')
    data_url = mio.imagefile_to_data_url('tests/data/fundus_image_small.bmp')
    assert data_url.startswith('data:image/bmp')
    data_url = mio.imagefile_to_data_url('tests/data/fundus_image_small.png')
    assert data_url.startswith('data:image/png')
    data_url = mio.imagefile_to_data_url('tests/data/fundus_image_small.tif')
    assert data_url.startswith('data:image/tif')


def test_imagefile_unknown_type():
    with pytest.raises(ValueError) as ex:
        mio.imagefile_to_data_url('tests/data/fundus_image_small.dataurl')
    assert 'Unknown image type:' in str(ex)


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
    assert 'Not a data URL' in str(ex)

    with pytest.raises(ValueError) as ex:
        data_url = 'data:image,/9j/4SXNRXhpZgAUAFFABRQB//Z'
        mio.parse_data_url(data_url)
    assert 'Data URL not in correct format' in str(ex)


def test_extract_image_and_type():
    data_url = open('tests/data/fundus_image_small.dataurl').read()
    data = mio.load_raw_image('tests/data/fundus_image_small.jpg')
    img_data, img_type = mio.extract_image_and_type(data_url)
    assert img_data == data
    assert img_type == 'jpg'


def test_extract_image_and_type_no_base64():
    data_url = 'data:image/jpg;base32,/9j/4SXNRXhpZgAUAFFABRQB//Z'
    with pytest.raises(ValueError) as ex:
        mio.extract_image_and_type(data_url)
    assert 'Not a base64 encoded image' in str(ex)
