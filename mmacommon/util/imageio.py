"""
.. module:: imageio
   :synopsis: Basic image IO operations such as saving, loading and encoding.
"""

import io
import base64
import numpy as np

from six.moves.urllib.request import urlopen
from PIL import Image as PilImage

# Map first two bytes of image to image format.
PREFIX2FMT = {(255, 216): 'jpg', (71, 73): 'gif', (137, 80): 'png',
              (66, 77): 'bmp', (73, 73): 'tif', (77, 77): 'tif'}


def save_raw_image(image, path):
    """
    Save raw image in binary format to specified path.

    Also see :py:func:`.load_raw_image`.

    :param raw image: Image of any type.
    :param str path: File path.
    """
    with open(path, 'wb') as f:
        f.write(image)


def load_raw_image(path):
    """
    Load raw image in binary format from specified path.

    Also see :py:func:`.save_raw_image`.

    :param str path: File path.
    :return: Raw image
    :rtype: str
    """
    with open(path, 'rb') as f:
        return f.read()


def image_from_url(url):
    """
    Load image from a URL (not a data url!)

    :param URL url: ULR, e.g. "https://www.ibm.com/image.png" or
                              "file:///your/file/image.png"
    :return: PIL Image
    :rtype: PIL.Image
    """
    fd = urlopen(url)
    image_file = io.BytesIO(fd.read())
    return PilImage.open(image_file)


def image_from_data_url(data_url):
    """
    Return PIL Image for data_url.
    :param data_url: Data URL for image, e.g.:
             'data:image/gif;base64,/9j/4SXNRXhpZgAUAFFABRQB//Z'
    :return: PIL Image
    :rtype: PIL.Image
    """
    image_data, _ = extract_image_and_type(data_url)
    buf = io.BytesIO(image_data)
    return PilImage.open(buf)


def pil_to_data_url(pil_image, fmt='png'):
    """
    Return data_url for PIL Image.
    :param pil_image: PIL image
    :param str fmt: Image format, e.g. jpg, tif, png, gif, bmp
    :return: data url with base64 encoded image
    :rtype: str
    """
    formats = {'jpg': 'JPEG', 'tif': 'TIFF'}
    buf = io.BytesIO()
    pil_fmt = formats.get(fmt, fmt.upper())
    pil_image.save(buf, format=pil_fmt)
    return image_to_data_url(buf.getvalue(), fmt)


def ndarray_to_data_url(image_array):
    """
    Return data URL that represents the image provided by the image_array.
    :param image_array: an ndarray containing an image
    :return: data url with base64 encoded image
    :rtype: str
    """
    image = PilImage.fromarray(image_array)
    return pil_to_data_url(image)


def ndarray_from_data_url(data_url, dtype=None):
    """
    Return numpy ndarray for image in data_url.
    :param data_url: Data URL for image, e.g.:
             'data:image/gif;base64,/9j/4SXNRXhpZgAUAFFABRQB//Z'
    :param dtype:  data-type, inferred if None
    :return: Image as numpy array
    :rtype: numpy.ndarray
    """
    return np.asarray(image_from_data_url(data_url), dtype)


def ndvolume_to_data_url(image_array):
    """
    Return data URL list that represents the image provided by the image_array.
    :param image_array: an ndvolume containing an image
    :return: data url list with base64 encoded image
    :rtype: str
    """
    return [pil_to_data_url(PilImage.fromarray(img)) for img in image_array]


def ndvolume_from_data_url(data_urls, dtype=None):
    """
    Return numpy ndvolume for images in data_list.
    :param data_urls: list of Data URLs for image, e.g.:
             ['data:image/gif;base64,/9j/4SXNRXhpZgAUAFFABRQB//Z',...]
    :param dtype:  data-type, inferred if None
    :return: Image as numpy array
    :rtype: numpy.ndarray
    """
    if not isinstance(data_urls, list):
        raise ValueError("Expected array of data URLs. Got: " + data_urls[:40])
    return np.stack(ndarray_from_data_url(url, dtype) for url in data_urls)


def imagefile_to_ndarray(path):
    """
    Gets the image from the given path as a numpy data array.

    :param str path: Path to image in binary format
    :return: the image as a numpy data array
    """
    data_url = imagefile_to_data_url(path)
    return ndarray_from_data_url(data_url)


def ndarray_to_imagefile(image, path):
    """
    Save ndarray as image file.

    :param ndarray image: Image as a numpy data array.
    :param str path: File path
    """
    im = PilImage.fromarray(image)
    im.save(path)


def image_to_data_url(image, fmt):
    """
    Return data URL for given raw image.

    :param str image: Raw binary image in some format.
    :param str fmt: Image format, e.g. jpg, tif, png, gif, bmp
    :return: Data URL for image, e.g.:
             'data:image/gif;base64,/9j/4SXNRXhpZgAUAFFABRQB//Z'
    :rtype: str
    """
    data = base64.b64encode(image).decode('utf-8')
    return 'data:image/{0};base64,{1}'.format(fmt, data)


def imagefile_to_data_url(path):
    """
    Read image in binary format and return data URL with base64 encoded image.

    Implementation based on:
    https://github.com/sindresorhus/file-type/blob/master/index.js
    http://www.fileformat.info/format/tiff/corion.htm

    :param str path: Path to image in binary format.
    :return: data URL, e.g. 'data:image/gif;base64,/9j/4SXNRXhpZg...AABRQB//Z'
    :rtype: str
    :raises: ValueError if file extension is missing.
    """

    def _extension(img):
        prefix = tuple(c if isinstance(c, int) else ord(c) for c in img[:2])
        try:
            return PREFIX2FMT[prefix]
        except KeyError:
            raise ValueError(
                'Unknown image type: ' + str(prefix) + ' : ' + path)

    img = load_raw_image(path)
    return image_to_data_url(img, _extension(img))


def parse_data_url(data_url):
    """
    Parses a data URL and returns its components.

    Data URLs are defined as follows::

       dataurl    := "data:" [ mediatype ] [ ";base64" ] "," data
       mediatype  := [ type "/" subtype ] *( ";" parameter )
       data       := *urlchar
       parameter  := attribute "=" value

    This specific implementation is limited to data urls of the following
    format::

        dataurl := "data:" type "/" subtype ";base64" "," data

    Here an example::
      'data:image/jpg;base64,/9j/4SXNRXhpZg...AUAFFABRQB//Z'

    References:

    - http://tools.ietf.org/html/rfc2397
    - http://www.askapache.com/online-tools/base64-image-converter/

    :param str data_url: A data URL.
    :return: Components of the data URL,
             e.g. ('image', 'png', 'base64', '/9j/4S')
    :rtype: tuple (datatype, subtype, encoding, data)
    :raises: ValueError if data URL doesn't follow spec.
    """
    if not data_url.startswith('data:'):
        raise ValueError("Not a data URL: " + data_url[:40])
    try:
        header, data = data_url.split(',')
        header = header.replace('data:', '')
        mediatype, encoding = header.rsplit(';', 1)
        datatype, subtype = mediatype.split('/')
    except:
        raise ValueError("Data URL not in correct format: " + data_url[:40])
    return datatype, subtype, encoding, data


def extract_image_and_type(data_url):
    """
    Returns raw image and type from a data url for a base64 encoded image.

    Data URLs for base64 encoded images are of the form::

      'data:image/jpg;base64,/9j/4SXNRXhpZg...AUAFFABRQB//Z'

    :param str data_url: Data URL for an image.
    :return: raw image and type, e.g. 'jpg'
    :rtype: tuple (raw_image, type)
    :raises: ValueError if data url doesn't contain base64 encoded image.
    """
    datatype, subtype, encoding, data = parse_data_url(data_url)
    if encoding != 'base64' or datatype != 'image':
        raise ValueError("Not a base64 encoded image: " + data_url[:50])
    return base64.b64decode(data), subtype
