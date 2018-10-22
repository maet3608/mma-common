"""
.. module:: orbitio
   :synopsis: Unit tests for orbitio
"""

import mmacommon.util.orbitio as oio
import pytest


@pytest.fixture(scope="function")
def input_data():
    image_url = 'data:image,/9j/4SXNRFABRQB//Z'
    in_data = {'data': {'image': image_url}}
    return in_data, image_url


@pytest.fixture(scope="function")
def input_data_array():
    image_url = 'data:image,/9j/4SXNRFABRQB//Z'
    in_data = {'data': {'image': [image_url, image_url, image_url]}}
    return in_data, image_url


oio.Registration.REGISTRATION_FILE = 'tests/data/registration.json'


def test_construct_orbitio():
    with pytest.raises(ValueError) as ex:
        oio.OrbitIO({})
    assert 'No input data!' in str(ex)

    with pytest.raises(ValueError) as ex:
        oio.OrbitIO("wrong input")
    assert 'Expect dictionary' in str(ex)


def test_logger(input_data):
    class Logger(object):
        def __init__(self):
            self.last_message = None

        def info(self, message):
            self.last_message = message

    logger = Logger()
    in_data, image_url = input_data
    oio.OrbitIO(in_data, logger)
    assert logger.last_message, 'Construction of OrbitIO should log message'


def test_read(input_data):
    in_data, image_url = input_data
    io = oio.OrbitIO(in_data)
    assert io.read('data/image') == image_url


def test_read_failure(input_data):
    with pytest.raises(ValueError) as ex:
        in_data, image_url = input_data
        io = oio.OrbitIO(in_data)
        io.read('data/imageid')
    assert 'Incorrect data path' in str(ex)


def test_read_array(input_data_array):
    in_data, image_url = input_data_array
    io = oio.OrbitIO(in_data)
    assert io.read('data/image', 1) == image_url
    assert type(io.read('data/image')) is list


def test_read_array_failure(input_data_array):
    in_data, image_url = input_data_array
    io = oio.OrbitIO(in_data)
    with pytest.raises(ValueError) as ex:
        io.read('data/imageid')
    assert 'Incorrect data path' in str(ex)
    with pytest.raises(IndexError) as ex:
        io.read('data/image', 5)
    assert 'list index out of range' in str(ex)


def test_write(input_data):
    in_data, image_url = input_data
    io = oio.OrbitIO(in_data)

    # path does not exist
    io.write('result/data/image', image_url)
    assert io.response() == {'result': {'data': {'image': image_url}}}

    # path already exists
    io.write('result/data/image', image_url)
    assert io.response() == {'result': {'data': {'image': image_url}}}

    # path exists partially
    io.write('result/data/number', 42)
    assert io.response() == {
        'result': {'data': {'image': image_url, 'number': 42}}}


def test_write_failure(input_data):
    with pytest.raises(ValueError) as ex:
        in_data, image_url = input_data
        io = oio.OrbitIO(in_data)
        io.write('', 42)
    assert 'Data path is empty!' in str(ex)


def test_write_geo(input_data):
    in_data, image_url = input_data
    io = oio.OrbitIO(in_data)
    io.write_geo('Point', [1.0, 2.0], label='A point')
    assert io.response() == {'image_annotations':
                                 {'result':
                                      {'type': 'FeatureCollection',
                                       'features': [
                                           {'geometry':
                                                {'type': 'Point',
                                                 'coordinates': [1.0, 2.0]},
                                            'type': 'Feature',
                                            'properties': {
                                                'label': 'A point'}}]}}}


def test_write_geo_failure(input_data):
    in_data, image_url = input_data
    io = oio.OrbitIO(in_data)
    with pytest.raises(ValueError) as ex:
        io.write_geo('Invalid', [1.0, 2.0])
    assert 'Invalid geo type' in str(ex)

    with pytest.raises(ValueError) as ex:
        io.write_geo('Point', [])
    assert 'Invalid coordinates' in str(ex)


def test_response_failure(input_data):
    with pytest.raises(ValueError) as ex:
        in_data, image_url = input_data
        io = oio.OrbitIO(in_data)
        io.response()
    assert 'No response available' in str(ex)


def test_construct_registration():
    oio.Registration()


@pytest.mark.skip(reason="Disabled until registration format has settled")
def test_check_required(input_data, monkeypatch):
    in_data, image_url = input_data
    registration = oio.Registration()
    registration.check_required(in_data)
    with pytest.raises(ValueError) as ex:
        registration.check_required({})
    assert 'Required input missing' in str(ex)

    # Checking when there are no requirements should be fine.
    oio.Registration.REGISTRATION_FILE = 'tests/data/registration_no_reqs.json'
    registration = oio.Registration()
    registration.check_required(in_data)


def test_worker_info():
    rego = oio.Registration()
    assert rego.worker_info() == 'Eye type detection (0.0.2)'
